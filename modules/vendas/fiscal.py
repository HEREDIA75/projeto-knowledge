import lxml.etree as ET
from signxml import XMLSigner, methods
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend


class AssinadorNFCe:
    def __init__(self, caminho_pfx: str, senha_pfx: str):
        self.caminho_pfx = caminho_pfx
        self.senha_pfx = senha_pfx.encode()
        self._carregar_certificado()

    def _carregar_certificado(self):
        with open(self.caminho_pfx, "rb") as f:
            pfx_data = f.read()

        self.private_key, self.cert, self.additional_certs = (
            pkcs12.load_key_and_certificates(
                pfx_data, self.senha_pfx, backend=default_backend()
            )
        )

    def assinar_xml_nfce(self, xml_string: str) -> str:
        """Assina o elemento XML da NFC-e mantendo o padrão W3C da SEFAZ."""
        root = ET.fromstring(xml_string.encode("utf-8"))

        signer = XMLSigner(
            method=methods.enveloped,
            signature_algorithm="rsa-sha1",
            digest_algorithm="sha1",
        )

        signed_root = signer.sign(
            root,
            key=self.private_key,
            cert=self.cert,
            reference_uri="#NFe"
            + root.find(".//{http://www.portalfiscal.inf.br/nfe}infNFe").attrib["Id"],
        )

        return ET.tostring(signed_root, encoding="utf-8").decode("utf-8")
