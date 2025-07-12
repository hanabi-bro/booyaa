from OpenSSL import crypto, SSL


crypto.load_certificate

rootca_crt_file = "cert_check/root-ca.crt"
rootca_key_file = "cert_check/root-ca.key"
rootca_passphrase = b"Gaia2020"

public_cacert_file = "cert_check/TEST_PrivateCA.cer"

with open(rootca_crt_file, 'rb') as f:
    rootca_cert_data = f.read()

with open(rootca_key_file, 'rb') as f:
    rootca_key_data = f.read()

with open(public_cacert_file, 'rb') as f:
    public_cacert_data = f.read()


rootca_obj = crypto.load_certificate(crypto.FILETYPE_PEM, rootca_cert_data)
rootca_key_obj = crypto.load_privatekey(crypto.FILETYPE_PEM, rootca_key_data, passphrase=rootca_passphrase)

public_cacert_obj = crypto.load_certificate(crypto.FILETYPE_PEM, public_cacert_data)

context = SSL.Context(SSL.TLSv1_METHOD)
context.use_certificate(rootca_obj)
context.use_privatekey(rootca_key_obj)

try:
    context.check_privatekey()
    print("OK")
except crypto.Error:
    print("NG")


print('Subject:', public_cacert_obj.get_subject())
print('Issuer:', public_cacert_obj.get_issuer())
print('Serial Number:', public_cacert_obj.get_serial_number())
print('Valid From:', public_cacert_obj.get_notBefore())
print('Valid To:', public_cacert_obj.get_notAfter())
