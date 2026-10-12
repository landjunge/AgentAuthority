/* Read-only own-client process identity + dynamic Apple code signature check. */
#include <CoreFoundation/CoreFoundation.h>
#include <Security/Security.h>
#include <libproc.h>
#include <sys/proc_info.h>
#include <sys/sysctl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void json_string(const char *s) {
    putchar('"');
    for (; *s; ++s) {
        unsigned char c = (unsigned char)*s;
        if (c == '"' || c == '\\') printf("\\%c", c);
        else if (c < 32) printf("\\u%04x", c);
        else putchar(c);
    }
    putchar('"');
}

static void cf_string(CFTypeRef value, char *out, size_t size) {
    out[0] = 0;
    if (value && CFGetTypeID(value) == CFStringGetTypeID())
        CFStringGetCString((CFStringRef)value, out, size, kCFStringEncodingUTF8);
}

int main(int argc, char **argv) {
    if (argc != 3) return 2;
    pid_t pid = (pid_t)strtol(argv[1], NULL, 10);
    struct proc_bsdinfo before = {0}, after = {0};
    char path_before[PROC_PIDPATHINFO_MAXSIZE] = {0}, path_after[PROC_PIDPATHINFO_MAXSIZE] = {0};
    int n1 = proc_pidinfo(pid, PROC_PIDTBSDINFO, 0, &before, sizeof(before));
    int p1 = proc_pidpath(pid, path_before, sizeof(path_before));
    CFNumberRef num = CFNumberCreate(NULL, kCFNumberIntType, &pid);
    const void *keys[] = {kSecGuestAttributePid};
    const void *values[] = {num};
    CFDictionaryRef attributes = CFDictionaryCreate(NULL, keys, values, 1,
        &kCFTypeDictionaryKeyCallBacks, &kCFTypeDictionaryValueCallBacks);
    SecCodeRef code = NULL;
    OSStatus guest = SecCodeCopyGuestWithAttributes(NULL, attributes, kSecCSDefaultFlags, &code);
    CFStringRef text = CFStringCreateWithCString(NULL, argv[2], kCFStringEncodingUTF8);
    SecRequirementRef requirement = NULL;
    OSStatus req = SecRequirementCreateWithString(text, kSecCSDefaultFlags, &requirement);
    OSStatus valid = guest ? guest : (req ? req : SecCodeCheckValidity(code, kSecCSStrictValidate, requirement));
    CFDictionaryRef information = NULL;
    OSStatus info = guest ? guest : SecCodeCopySigningInformation(code, kSecCSSigningInformation, &information);
    char team[100] = {0}, identifier[200] = {0}, cdhash[129] = {0};
    if (!info) {
        cf_string(CFDictionaryGetValue(information, kSecCodeInfoTeamIdentifier), team, sizeof(team));
        cf_string(CFDictionaryGetValue(information, kSecCodeInfoIdentifier), identifier, sizeof(identifier));
        CFDataRef hash = CFDictionaryGetValue(information, kSecCodeInfoUnique);
        if (hash && CFGetTypeID(hash) == CFDataGetTypeID() && CFDataGetLength(hash) <= 64)
            for (CFIndex i = 0; i < CFDataGetLength(hash); i++)
                snprintf(cdhash + i * 2, 3, "%02x", CFDataGetBytePtr(hash)[i]);
    }
    int n2 = proc_pidinfo(pid, PROC_PIDTBSDINFO, 0, &after, sizeof(after));
    int p2 = proc_pidpath(pid, path_after, sizeof(path_after));
    struct timeval boot = {0}; size_t boot_size = sizeof(boot);
    int boot_status = sysctlbyname("kern.boottime", &boot, &boot_size, NULL, 0);
    int stable = n1 == sizeof(before) && n2 == sizeof(after) && p1 > 0 && p2 > 0 &&
        before.pbi_pid == (unsigned)pid && after.pbi_pid == (unsigned)pid &&
        before.pbi_start_tvsec == after.pbi_start_tvsec && before.pbi_start_tvusec == after.pbi_start_tvusec &&
        !strcmp(path_before, path_after);
    printf("{\"pid\":%d,\"ppid\":%u,\"uid\":%u,\"start_sec\":%llu,\"start_usec\":%llu,",
        pid, before.pbi_ppid, before.pbi_uid, (unsigned long long)before.pbi_start_tvsec,
        (unsigned long long)before.pbi_start_tvusec);
    printf("\"boot_sec\":%lld,\"boot_read_status\":%d,\"kernel_instance_stable\":%s,",
        (long long)boot.tv_sec, boot_status, stable ? "true" : "false");
    printf("\"proc_info_bytes\":[%d,%d],\"proc_path_status\":[%d,%d],", n1, n2, p1, p2);
    printf("\"guest_status\":%d,\"requirement_status\":%d,\"validity_status\":%d,\"signing_info_status\":%d,",
        (int)guest, (int)req, (int)valid, (int)info);
    printf("\"path\":"); json_string(path_before);
    printf(",\"team\":"); json_string(team);
    printf(",\"identifier\":"); json_string(identifier);
    printf(",\"cdhash\":"); json_string(cdhash);
    printf(",\"anchor\":\"Apple generic signing chain plus pinned vendor requirement\"}\n");
    if (information) CFRelease(information);
    if (code) CFRelease(code);
    if (requirement) CFRelease(requirement);
    CFRelease(text); CFRelease(attributes); CFRelease(num);
    return 0; /* Qualification is explicit in fields, not hidden in process status. */
}
