/* Availability only: no event subscriptions, writer attribution or privilege changes. */
#include <EndpointSecurity/EndpointSecurity.h>
#include <bsm/libbsm.h>
#include <errno.h>
#include <fcntl.h>
#include <libproc.h>
#include <mach/mach.h>
#include <stdio.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

static long long ns(const struct timespec *t) {
    return (long long)t->tv_sec * 1000000000LL + t->tv_nsec;
}

static double seconds(const struct timeval *t) {
    return t->tv_sec + t->tv_usec / 1000000.0;
}

int main(int argc, char **argv) {
    if (argc != 2 || geteuid() == 0) return 64;
    struct rusage before = {0}, after = {0};
    struct timespec start = {0}, end = {0};
    int resource_before = getrusage(RUSAGE_SELF, &before);
    int clock_before = clock_gettime(CLOCK_MONOTONIC, &start);
    pid_t pid = getpid();
    struct proc_bsdinfo first = {0}, last = {0};
    errno = 0;
    int bsd_n = proc_pidinfo(pid, PROC_PIDTBSDINFO, 0, &first, sizeof(first));
    int bsd_errno = errno;

    int fd = open(argv[1], O_RDONLY | O_NOFOLLOW);
    int fd_open_errno = fd < 0 ? errno : 0;
    struct stat st = {0};
    int stat_rc = fd < 0 ? -1 : fstat(fd, &st);
    struct vnode_fdinfowithpath vnode = {0};
    errno = 0;
    int fd_n = fd < 0 ? 0 : proc_pidfdinfo(pid, fd, PROC_PIDFDVNODEPATHINFO,
                                         &vnode, sizeof(vnode));
    int fd_errno = fd < 0 ? fd_open_errno : errno;
    int file_ok = fd_n == sizeof(vnode) && stat_rc == 0 && S_ISREG(st.st_mode);
    int same_file = file_ok && (uint32_t)st.st_dev == vnode.pvip.vip_vi.vi_stat.vst_dev &&
                    (uint64_t)st.st_ino == vnode.pvip.vip_vi.vi_stat.vst_ino;
    if (fd >= 0) close(fd);

    audit_token_t token = {{0}};
    mach_msg_type_number_t token_count = TASK_AUDIT_TOKEN_COUNT;
    kern_return_t task_rc = task_info(mach_task_self(), TASK_AUDIT_TOKEN,
                                      (task_info_t)&token, &token_count);
    int token_ok = task_rc == KERN_SUCCESS && token_count == TASK_AUDIT_TOKEN_COUNT;

    int condition = 0;
    errno = 0;
    int audit_rc = auditon(A_GETCOND, &condition, sizeof(condition));
    int audit_errno = errno;
    struct stat pipe_st = {0};
    errno = 0;
    int pipe_stat_rc = stat("/dev/auditpipe", &pipe_st);
    int pipe_stat_errno = errno;
    errno = 0;
    int pipe_fd = open("/dev/auditpipe", O_RDONLY | O_NONBLOCK);
    int pipe_errno = pipe_fd < 0 ? errno : 0;
    if (pipe_fd >= 0) close(pipe_fd); /* Never read or configure audit records. */

    es_client_t *client = NULL;
    __block unsigned int callbacks = 0;
    es_new_client_result_t es_rc = es_new_client(&client,
        ^(es_client_t *c, const es_message_t *m) {
            (void)c; (void)m; callbacks++;
        });
    int connected = es_rc == ES_NEW_CLIENT_RESULT_SUCCESS;
    int cleanup = connected ? es_delete_client(client) : -1;
    /* No subscribe/respond/mute/cache/TCC/entitlement operation exists here. */

    errno = 0;
    int bsd_last_n = proc_pidinfo(pid, PROC_PIDTBSDINFO, 0, &last, sizeof(last));
    int bsd_last_errno = errno;
    int stable = bsd_n == sizeof(first) && bsd_last_n == sizeof(last) &&
                 first.pbi_pid == (uint32_t)pid && last.pbi_pid == first.pbi_pid &&
                 first.pbi_uid == last.pbi_uid &&
                 first.pbi_start_tvsec == last.pbi_start_tvsec &&
                 first.pbi_start_tvusec == last.pbi_start_tvusec;
    int resource_after = getrusage(RUSAGE_SELF, &after);
    int clock_after = clock_gettime(CLOCK_MONOTONIC, &end);
    int metrics_ok = resource_before == 0 && resource_after == 0;
    unsigned long api_bytes = (bsd_n == sizeof(first) ? sizeof(first) : 0) +
        (bsd_last_n == sizeof(last) ? sizeof(last) : 0) +
        (fd_n == sizeof(vnode) ? sizeof(vnode) : 0) +
        (token_ok ? sizeof(token) : 0) + (audit_rc == 0 ? sizeof(condition) : 0);

    printf("{\"schema\":\"a1-native-availability-v1\",\"euid\":%u,", geteuid());
    printf("\"bsd\":{\"returned\":%d,\"expected\":%lu,\"errno\":%d,"
           "\"after_returned\":%d,\"after_errno\":%d,\"stable\":%s,"
           "\"pid\":%u,\"uid\":%u,\"start_seconds\":%llu,\"start_microseconds\":%llu},",
           bsd_n, sizeof(first), bsd_errno, bsd_last_n, bsd_last_errno,
           stable ? "true" : "false", first.pbi_pid, first.pbi_uid,
           first.pbi_start_tvsec, first.pbi_start_tvusec);
    printf("\"fd\":{\"returned\":%d,\"expected\":%lu,\"errno\":%d,"
           "\"same_file\":%s,\"read_only\":true,\"device\":%u,\"inode\":%llu,"
           "\"generation\":%u,\"kernel_openflags\":%u},",
           fd_n, sizeof(vnode), fd_errno, same_file ? "true" : "false",
           vnode.pvip.vip_vi.vi_stat.vst_dev, vnode.pvip.vip_vi.vi_stat.vst_ino,
           vnode.pvip.vip_vi.vi_stat.vst_gen, vnode.pfi.fi_openflags);
    printf("\"mach\":{\"return\":%d,\"count\":%u,\"expected_count\":%u,"
           "\"pid\":%d,\"pid_version\":%d},", task_rc, token_count,
           (unsigned int)TASK_AUDIT_TOKEN_COUNT, token_ok ? audit_token_to_pid(token) : -1,
           token_ok ? audit_token_to_pidversion(token) : -1);
    printf("\"audit\":{\"return\":%d,\"errno\":%d,\"condition\":%d},",
           audit_rc, audit_errno, condition);
    printf("\"auditpipe\":{\"stat_return\":%d,\"stat_errno\":%d,\"mode\":%u,"
           "\"owner_uid\":%u,\"opened\":%s,\"errno\":%d,\"records_read\":0},",
           pipe_stat_rc, pipe_stat_errno, pipe_st.st_mode & 07777, pipe_st.st_uid,
           pipe_fd >= 0 ? "true" : "false", pipe_errno);
    printf("\"es\":{\"result\":%d,\"not_entitled_code\":%d,\"not_permitted_code\":%d,"
           "\"not_privileged_code\":%d,\"connected\":%s,\"cleanup_return\":%d,"
           "\"callbacks\":%u,\"subscriptions\":0},", es_rc,
           ES_NEW_CLIENT_RESULT_ERR_NOT_ENTITLED, ES_NEW_CLIENT_RESULT_ERR_NOT_PERMITTED,
           ES_NEW_CLIENT_RESULT_ERR_NOT_PRIVILEGED, connected ? "true" : "false",
           cleanup, callbacks);
    printf("\"metrics\":{\"api_response_bytes\":%lu,\"resource_ok\":%s,"
           "\"cpu_user_seconds\":%.9f,\"cpu_system_seconds\":%.9f,"
           "\"peak_rss_bytes\":%ld,\"clock_ok\":%s,\"elapsed_ns\":%lld}}\n",
           api_bytes, metrics_ok ? "true" : "false",
           seconds(&after.ru_utime) - seconds(&before.ru_utime),
           seconds(&after.ru_stime) - seconds(&before.ru_stime), after.ru_maxrss,
           clock_before == 0 && clock_after == 0 ? "true" : "false", ns(&end)-ns(&start));
    return connected ? 65 : 0;
}
