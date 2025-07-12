from OpenSSL import SSL, crypto

privateca_file = "cert_check/TEST_privateCA.cer"

# 自己署名のCA証明書を読み込む
with open(privateca_file, "rb") as f:
    ca_cert_data = f.read()
ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_cert_data)

# コールバック関数の定義
def verify_callback(conn, cert, errno, depth, preverify_ok):
    # 自己署名のCA証明書として検証する
    if depth == 0 and preverify_ok:
        return cert.get_issuer().as_der() == ca_cert.get_subject().as_der()
    return preverify_ok

# SSLコンテキストを作成し、コールバック関数を設定
context = SSL.Context(SSL.TLSv1_METHOD)
context.set_verify(SSL.VERIFY_PEER, verify_callback)


# サーバ証明書を読み込む
with open("cert_check/_.badssl.com.crt", "rb") as f:
    server_cert_data = f.read()
server_cert = crypto.load_certificate(crypto.FILETYPE_PEM, server_cert_data)


store = crypto.X509Store()

store_ctx = crypto.X509StoreContext(store, server_cert)
try:
    store_ctx.verify_certificate()
    print("サーバ証明書は信頼されるCAから発行されています。")
except crypto.X509StoreContextError:
    print("サーバ証明書は信頼されるCAから発行されていません。")


for i in store.get_certs():
    print(i)