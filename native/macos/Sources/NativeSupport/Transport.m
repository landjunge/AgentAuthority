#include "NativeSupport.h"
#include <xpc/xpc.h>
#include <dispatch/dispatch.h>
#include <string.h>

// macOS 12 public peer requirement binds the kernel's actual XPC sender,
// avoiding PID-based code-signature checks and PID-reuse races.
void aa_rpc_request(const char *service, const char *requirement, const char *json, aa_reply_handler reply) {
    dispatch_queue_t queue = dispatch_queue_create("de.agentauthority.rpc", DISPATCH_QUEUE_SERIAL);
    __block xpc_connection_t c = xpc_connection_create_mach_service(service, queue, XPC_CONNECTION_MACH_SERVICE_PRIVILEGED);
    if (!c || xpc_connection_set_peer_code_signing_requirement(c, requirement) != 0) {
        reply("{\"error\":\"peer_requirement\"}"); return;
    }
    __block int done = 0;
    __block dispatch_source_t timer = dispatch_source_create(DISPATCH_SOURCE_TYPE_TIMER, 0, 0, queue);
    dispatch_source_set_cancel_handler(timer, ^{ timer=nil; c=nil; });
    dispatch_source_set_timer(timer, dispatch_time(DISPATCH_TIME_NOW, 5*NSEC_PER_SEC), DISPATCH_TIME_FOREVER, 0);
    dispatch_source_set_event_handler(timer, ^{
        if (!done) {done=1; reply("{\"error\":\"timeout\"}");xpc_connection_cancel(c);}
        dispatch_source_cancel(timer);
    });
    xpc_connection_set_event_handler(c, ^(xpc_object_t event) {
        if (xpc_get_type(event)==XPC_TYPE_ERROR && !done) {
            done=1; reply("{\"error\":\"unavailable\"}");dispatch_source_cancel(timer);xpc_connection_cancel(c);
        }
    });
    xpc_connection_resume(c);dispatch_resume(timer);
    xpc_object_t message=xpc_dictionary_create(NULL,NULL,0);
    xpc_dictionary_set_string(message,"json",json);
    xpc_connection_send_message_with_reply(c,message,queue,^(xpc_object_t response){
        if(done)return;done=1;dispatch_source_cancel(timer);
        const char *text=xpc_get_type(response)==XPC_TYPE_DICTIONARY ? xpc_dictionary_get_string(response,"json"):NULL;
        if(text && strlen(text)<=1024*1024)reply(text);else reply("{\"error\":\"response\"}");
        xpc_connection_cancel(c);
    });
}
