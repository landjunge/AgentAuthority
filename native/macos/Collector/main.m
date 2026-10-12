#import <Foundation/Foundation.h>
#import <EndpointSecurity/EndpointSecurity.h>
#import <Security/Security.h>
#import <bsm/libbsm.h>
#import <xpc/xpc.h>
#import <sys/sysctl.h>
#import <mach/mach_time.h>

static NSLock *lock;
static NSMutableArray<NSDictionary *> *records;
static es_client_t *client;
static es_new_client_result_t esResult;
static uint64_t lastGlobal=0, sequenceGaps=0, sequenceInvalid=0, bufferDropped=0, scopeID=0;
static BOOL globalSeen=NO, scopeActive=NO, sequenceAvailable=NO;
static uint64_t device=0,inode=0;
static uid_t ownerUID;
static NSTimeInterval expires=0;
static uint64_t scopeStartMach=0,scopeDeadlineMach=0;
static mach_timebase_info_data_t timebase;
static struct timeval bootTime;

static NSString *stringToken(es_string_token_t token) {
    size_t length=MIN(token.length,256);
    return [[NSString alloc] initWithBytes:token.data length:length encoding:NSUTF8StringEncoding] ?: @"";
}
static void observe(const es_message_t *m) {
    @autoreleasepool {
        [lock lock];
        if(m->version>=4){
            if(globalSeen && m->global_seq_num>lastGlobal+1 && scopeActive) sequenceGaps+=m->global_seq_num-lastGlobal-1;
            if(globalSeen && m->global_seq_num<=lastGlobal && scopeActive)sequenceInvalid++;
            lastGlobal=m->global_seq_num;globalSeen=YES;
        }else if(scopeActive){sequenceAvailable=NO;}
        if(!scopeActive || mach_continuous_time()>scopeDeadlineMach){scopeActive=NO;[lock unlock];return;}
        if(m->mach_time<scopeStartMach){[lock unlock];return;}
        const es_process_t *p=m->process;
        if(audit_token_to_euid(p->audit_token)!=ownerUID){[lock unlock];return;}
        es_file_t *target=NULL;NSString *event=nil;
        switch(m->event_type){
            case ES_EVENT_TYPE_NOTIFY_WRITE:target=m->event.write.target;event=@"write";break;
            case ES_EVENT_TYPE_NOTIFY_CLOSE:target=m->event.close.target;event=@"close";break;
            case ES_EVENT_TYPE_NOTIFY_EXEC:event=@"exec";p=m->event.exec.target;break;
            case ES_EVENT_TYPE_NOTIFY_FORK:event=@"fork";p=m->event.fork.child;break;
            case ES_EVENT_TYPE_NOTIFY_EXIT:event=@"exit";break;
            default:[lock unlock];return;
        }
        if(target && ((uint64_t)target->stat.st_dev!=device || target->stat.st_ino!=inode)){[lock unlock];return;}
        if(records.count>=5000){bufferDropped++;[lock unlock];return;}
        NSMutableDictionary *r=[@{
            @"event":event,@"pid":@(audit_token_to_pid(p->audit_token)),@"pid_version":@(audit_token_to_pidversion(p->audit_token)),
            @"uid":@(audit_token_to_euid(p->audit_token)),@"ppid":@(p->ppid),@"version":@(m->version),
            @"mach_time":@(m->mach_time),@"event_time_sec":@(m->time.tv_sec),@"event_time_nsec":@(m->time.tv_nsec),
            @"boot_sec":@(bootTime.tv_sec),@"boot_usec":@(bootTime.tv_usec),@"scope_id":@(scopeID),
            @"signing_id":stringToken(p->signing_id),@"codesigning_flags":@(p->codesigning_flags)
        } mutableCopy];
        if(m->version>=3){r[@"start_sec"]=@(p->start_time.tv_sec);r[@"start_usec"]=@(p->start_time.tv_usec);}
        if(m->version>=4){r[@"global_sequence"]=@(m->global_seq_num);}
        if(m->version>=2){r[@"event_sequence"]=@(m->seq_num);}
        if(target){r[@"dev"]=@((uint64_t)target->stat.st_dev);r[@"inode"]=@(target->stat.st_ino);}
        if(m->event_type==ES_EVENT_TYPE_NOTIFY_CLOSE){r[@"modified"]=@(m->event.close.modified);}
        [records addObject:r];[lock unlock];
    }
}
static NSDictionary *handle(NSDictionary *request,uid_t uid) {
    NSString *command=request[@"command"];
    if(![command isKindOfClass:NSString.class])return @{@"error":@"command"};
    [lock lock];NSDictionary *reply;
    if(scopeActive && mach_continuous_time()>scopeDeadlineMach)scopeActive=NO;
    if([command isEqualToString:@"status"]){reply=@{@"es_result":@(esResult),@"sequence_seeded":@(globalSeen),@"observer_only":@YES};}
    else if(esResult!=ES_NEW_CLIENT_RESULT_SUCCESS){reply=@{@"error":@"source_unavailable"};}
    else if([command isEqualToString:@"scope"]){
        id dev=request[@"dev"],ino=request[@"inode"];
        if(![dev isKindOfClass:NSNumber.class]||![ino isKindOfClass:NSNumber.class]||[ino unsignedLongLongValue]==0||scopeActive){reply=@{@"error":@"scope"};}
        else{device=[dev unsignedLongLongValue];inode=[ino unsignedLongLongValue];ownerUID=uid;scopeID++;scopeActive=YES;scopeStartMach=mach_absolute_time();scopeDeadlineMach=mach_continuous_time()+(uint64_t)(15.0*NSEC_PER_SEC*timebase.denom/timebase.numer);expires=NSDate.timeIntervalSinceReferenceDate+15;sequenceGaps=0;sequenceInvalid=0;bufferDropped=0;sequenceAvailable=globalSeen;[records removeAllObjects];reply=@{@"scope_id":@(scopeID),@"sequence_available":@(sequenceAvailable)};}
    }else if(uid!=ownerUID){reply=@{@"error":@"scope_owner"};}
    else if([command isEqualToString:@"events"]){reply=@{@"scope_id":@(scopeID),@"events":[records copy],@"sequence_gaps":@(sequenceGaps),@"sequence_invalid":@(sequenceInvalid),@"buffer_dropped":@(bufferDropped),@"sequence_available":@(sequenceAvailable),@"scope_active":@(scopeActive),@"expires":@(expires),@"provider_identity":@"UNBEKANNT",@"durable_effect":@"UNBEKANNT"};}
    else if([command isEqualToString:@"end"]){scopeActive=NO;reply=@{@"ended":@YES};}
    else{reply=@{@"error":@"command"};}
    [lock unlock];return reply;
}
int main(int argc,const char *argv[]) {
    @autoreleasepool {
        lock=[NSLock new];records=[NSMutableArray new];size_t size=sizeof(bootTime);
        if(mach_timebase_info(&timebase)!=KERN_SUCCESS || timebase.numer==0)return 78;
        if(sysctlbyname("kern.boottime",&bootTime,&size,NULL,0)!=0)memset(&bootTime,0,sizeof(bootTime));
        esResult=es_new_client(&client,^(es_client_t *unused,const es_message_t *message){(void)unused;observe(message);});
        if(argc==2 && strcmp(argv[1],"--diagnose")==0){printf("{\"es_result\":%u,\"euid\":%u,\"observer_only\":true}\n",(unsigned)esResult,(unsigned)geteuid());if(client)es_delete_client(client);return 0;}
        if(esResult==ES_NEW_CLIENT_RESULT_SUCCESS){
            const es_event_type_t subscriptions[]={ES_EVENT_TYPE_NOTIFY_WRITE,ES_EVENT_TYPE_NOTIFY_CLOSE,ES_EVENT_TYPE_NOTIFY_EXEC,ES_EVENT_TYPE_NOTIFY_FORK,ES_EVENT_TYPE_NOTIFY_EXIT};
            if(es_subscribe(client,subscriptions,5)!=ES_RETURN_SUCCESS){es_delete_client(client);client=NULL;esResult=ES_NEW_CLIENT_RESULT_ERR_INTERNAL;}
        }
        NSString *team=[NSBundle.mainBundle objectForInfoDictionaryKey:@"AAExpectedTeam"];
        if(![team isKindOfClass:NSString.class] || [team rangeOfString:@"^[A-Z0-9]{10}$" options:NSRegularExpressionSearch].location==NSNotFound)return 78;
        NSString *name=[NSString stringWithFormat:@"%@.de.agentauthority.observer.collector.xpc",team];
        NSString *requirement=[NSString stringWithFormat:@"anchor apple generic and identifier \"de.agentauthority.observer\" and certificate leaf[subject.OU] = \"%@\"",team];
        dispatch_queue_t queue=dispatch_queue_create("de.agentauthority.collector.rpc",DISPATCH_QUEUE_SERIAL);
        xpc_connection_t listener=xpc_connection_create_mach_service(name.UTF8String,queue,XPC_CONNECTION_MACH_SERVICE_LISTENER);
        if(!listener || xpc_connection_set_peer_code_signing_requirement(listener,requirement.UTF8String)!=0)return 78;
        xpc_connection_set_event_handler(listener,^(xpc_object_t incoming){
            if(xpc_get_type(incoming)!=XPC_TYPE_CONNECTION)return;
            __block xpc_connection_t peer=incoming;
            uid_t uid=xpc_connection_get_euid(peer);
            xpc_connection_set_event_handler(peer,^(xpc_object_t message){
                @autoreleasepool{
                    if(xpc_get_type(message)==XPC_TYPE_ERROR){xpc_connection_cancel(peer);peer=nil;return;}
                    if(xpc_get_type(message)!=XPC_TYPE_DICTIONARY)return;
                    const char *text=xpc_dictionary_get_string(message,"json");if(!text||strlen(text)>65536)return;
                    NSData *data=[NSData dataWithBytes:text length:strlen(text)];id request=[NSJSONSerialization JSONObjectWithData:data options:0 error:NULL];
                    NSDictionary *response=[request isKindOfClass:NSDictionary.class] ? handle(request,uid):@{@"error":@"json"};
                    NSData *encoded=[NSJSONSerialization dataWithJSONObject:response options:0 error:NULL];
                    NSString *body=[[NSString alloc] initWithData:encoded encoding:NSUTF8StringEncoding];xpc_object_t reply=xpc_dictionary_create_reply(message);if(!reply)return;
                    xpc_dictionary_set_string(reply,"json",body.UTF8String);xpc_connection_send_message(peer,reply);
                }
            });xpc_connection_resume(peer);
        });xpc_connection_resume(listener);dispatch_main();
    }
}
