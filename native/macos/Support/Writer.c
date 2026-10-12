#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <libproc.h>
#include <sys/proc_info.h>
#include <mach/mach.h>

static int execute(const char *mode,const char *path) {
    int wrote=0,fd=-1;struct stat file={0};
    if(strcmp(mode,"idle")){fd=open(path,O_WRONLY|O_NOFOLLOW);if(fd<0)return 2;if(fstat(fd,&file)!=0){close(fd);return 2;}
        const char payload[]="AA-test-evidence";if(write(fd,payload,sizeof(payload)-1)!=(ssize_t)(sizeof(payload)-1)){close(fd);return 2;}wrote=1;close(fd);
    }
    struct proc_bsdinfo info={0};int bytes=proc_pidinfo(getpid(),PROC_PIDTBSDINFO,0,&info,sizeof(info));
    audit_token_t token={0};mach_msg_type_number_t count=TASK_AUDIT_TOKEN_COUNT;
    kern_return_t audit_status=task_info(mach_task_self(),TASK_AUDIT_TOKEN,(task_info_t)&token,&count);
    printf("{\"writer_pid\":%d,\"pid_version\":%u,\"start_sec\":%llu,\"start_usec\":%llu,\"bsd_bytes\":%d,\"audit_status\":%d,\"target_write\":%s,\"dev\":%llu,\"inode\":%llu,\"claimed_pid\":%d}\n",getpid(),token.val[7],(unsigned long long)info.pbi_start_tvsec,(unsigned long long)info.pbi_start_tvusec,bytes,audit_status,wrote?"true":"false",(unsigned long long)file.st_dev,(unsigned long long)file.st_ino,!strcmp(mode,"forged")?999999:getpid());
    return 0;
}
int main(int argc,char *argv[]) {
    if(argc!=3 || (strcmp(argv[1],"write")&&strcmp(argv[1],"idle")&&strcmp(argv[1],"child")&&strcmp(argv[1],"forged")))return 2;
    if(!strcmp(argv[1],"child")){pid_t child=fork();if(child<0)return 2;if(child==0){int result=execute("write",argv[2]);fflush(stdout);_exit(result);}int status=0;if(waitpid(child,&status,0)<0)return 2;return WIFEXITED(status)?WEXITSTATUS(status):2;}
    return execute(argv[1],argv[2]);
}
