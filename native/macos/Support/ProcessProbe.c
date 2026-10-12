#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <libproc.h>
#include <sys/proc_info.h>
#include <sys/sysctl.h>
#include <mach/mach.h>
#include <EndpointSecurity/EndpointSecurity.h>

int main(void) {
    struct proc_bsdinfo info={0};
    int bytes=proc_pidinfo(getpid(),PROC_PIDTBSDINFO,0,&info,sizeof(info));
    struct timeval boot={0};size_t size=sizeof(boot);
    int boot_status=sysctlbyname("kern.boottime",&boot,&size,NULL,0);
    audit_token_t token={0};mach_msg_type_number_t count=TASK_AUDIT_TOKEN_COUNT;
    kern_return_t audit_status=task_info(mach_task_self(),TASK_AUDIT_TOKEN,(task_info_t)&token,&count);
    es_client_t *client=NULL;
    es_new_client_result_t es_status=es_new_client(&client,^(es_client_t *c,const es_message_t *m){(void)c;(void)m;});
    if(client)es_delete_client(client);
    printf("{\"schema\":\"agent-authority-process-probe-v1\",\"pid\":%d,\"ppid\":%u,\"uid\":%u,\"bsd_bytes\":%d,\"start_sec\":%llu,\"start_usec\":%llu,\"boot_sec\":%lld,\"boot_status\":%d,\"audit_status\":%d,\"pid_version\":%u,\"es_result\":%u,\"writer_attribution\":\"UNBEKANNT\",\"provider_identity\":\"UNBEKANNT\"}\n",
        getpid(),info.pbi_ppid,geteuid(),bytes,(unsigned long long)info.pbi_start_tvsec,(unsigned long long)info.pbi_start_tvusec,(long long)boot.tv_sec,boot_status,audit_status,token.val[7],(unsigned)es_status);
    return 0;
}
