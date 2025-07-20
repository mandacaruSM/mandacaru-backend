import cv2
import json

def ler_qr_code(caminho_imagem):
    try:
        imagem = cv2.imread(str(caminho_imagem))
        if imagem is None:
            print(f"[QR ERRO] Imagem não encontrada: {caminho_imagem}")
            return None

        detector = cv2.QRCodeDetector()
        dados, _, _ = detector.detectAndDecode(imagem)
        if dados:
            return json.loads(dados)
        else:
            print("[QR ERRO] Nenhum dado detectado no QR Code.")
            return None
    except json.JSONDecodeError as e:
        print(f"[QR ERRO] Falha ao decodificar JSON: {e}")
        return None
    except Exception as e:
        print(f"[QR ERRO] Erro inesperado: {e}")
        return None
