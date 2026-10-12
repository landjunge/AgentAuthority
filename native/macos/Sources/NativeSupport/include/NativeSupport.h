#include <stddef.h>
typedef void (^aa_reply_handler)(const char *json);
void aa_rpc_request(const char *service, const char *requirement, const char *json, aa_reply_handler reply);
