"""OpenSSL 3 EVP primitives, in memory; no message/secret tempfiles or subprocess argv.

Uses the already installed OpenSSL library, Ed25519 envelopes unchanged, and
AES-256-GCM (96-bit random nonce, 128-bit tag). No custom cipher construction.
"""

import base64
import ctypes as c
import ctypes.util
import secrets
from pathlib import Path

from research.a2_linux.protocol import canonical


def function(name, result, *args):
    fn = getattr(LIB, name)
    fn.restype, fn.argtypes = result, list(args)
    return fn


LIB = c.CDLL(ctypes.util.find_library("crypto"))
P, I, Z = c.c_void_p, c.c_int, c.c_size_t
new_cipher = function("EVP_CIPHER_CTX_new", P)
free_cipher = function("EVP_CIPHER_CTX_free", None, P)
aes_gcm = function("EVP_aes_256_gcm", P)
init = function("EVP_CipherInit_ex", I, P, P, P, P, P, I)
update = function("EVP_CipherUpdate", I, P, P, P, P, I)
final = function("EVP_CipherFinal_ex", I, P, P, P)
ctrl = function("EVP_CIPHER_CTX_ctrl", I, P, I, I, P)
new_md = function("EVP_MD_CTX_new", P)
free_md = function("EVP_MD_CTX_free", None, P)
free_key = function("EVP_PKEY_free", None, P)
new_public = function("EVP_PKEY_new_raw_public_key_ex", P, P, c.c_char_p, P, P, Z)
new_bio = function("BIO_new_mem_buf", P, P, I)
free_bio = function("BIO_free", I, P)
read_private = function("PEM_read_bio_PrivateKey", P, P, P, P, P)
sign_init = function("EVP_DigestSignInit", I, P, P, P, P, P)
sign_bytes = function("EVP_DigestSign", I, P, P, P, P, Z)
verify_init = function("EVP_DigestVerifyInit", I, P, P, P, P, P)
verify_bytes = function("EVP_DigestVerify", I, P, P, Z, P, Z)


def check(value):
    if value != 1:
        raise ValueError("CRYPTO_FAILED")


def crypt(key, raw, aad, encrypt):
    if len(key) != 32 or (not encrypt and len(raw) < 28):
        raise ValueError("CIPHERTEXT_INVALID")
    nonce = secrets.token_bytes(12) if encrypt else raw[:12]
    data = raw if encrypt else raw[12:-16]
    ctx = new_cipher()
    if not ctx:
        raise ValueError("CRYPTO_FAILED")
    out, size, tail = c.create_string_buffer(len(data) + 16), I(), I()
    try:
        check(init(ctx, aes_gcm(), None, key, nonce, int(encrypt)))
        check(update(ctx, None, c.byref(size), aad, len(aad)))
        check(update(ctx, out, c.byref(size), data, len(data)))
        if not encrypt:
            tag = c.create_string_buffer(raw[-16:])
            check(ctrl(ctx, 0x11, 16, tag))
        check(final(ctx, c.byref(out, size.value), c.byref(tail)))
        result = out.raw[: size.value + tail.value]
        if encrypt:
            tag = c.create_string_buffer(16)
            check(ctrl(ctx, 0x10, 16, tag))
            result = nonce + result + tag.raw
        return result
    finally:
        free_cipher(ctx)


def sign(keyfile, body):
    raw = Path(keyfile).read_bytes()
    bio = new_bio(raw, len(raw))
    key = read_private(bio, None, None, None)
    ctx = new_md()
    try:
        if not key or not ctx:
            raise ValueError("KEY_INVALID")
        check(sign_init(ctx, None, None, None, key))
        signature, size = c.create_string_buffer(64), Z(64)
        message = canonical(body)
        check(sign_bytes(ctx, signature, c.byref(size), message, len(message)))
        if size.value != 64:
            raise ValueError("SIGNATURE_INVALID")
        return {"body": body, "signature": base64.b64encode(signature.raw).decode()}
    finally:
        free_md(ctx)
        free_key(key)
        free_bio(bio)


def verify(public_key, packet):
    key, ctx = None, None
    try:
        raw = base64.b64decode(public_key, validate=True)
        if len(raw) != 32:
            return False
        key = new_public(None, b"ED25519", None, raw, len(raw))
        ctx = new_md()
        if not key or not ctx:
            return False
        check(verify_init(ctx, None, None, None, key))
        message = canonical(packet["body"])
        signature = base64.b64decode(packet["signature"], validate=True)
        return verify_bytes(ctx, signature, len(signature), message, len(message)) == 1
    except (ValueError, TypeError, KeyError):
        return False
    finally:
        free_md(ctx)
        free_key(key)
