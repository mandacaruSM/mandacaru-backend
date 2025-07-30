
from django.core.management.base import BaseCommand
from backend.apps.equipamentos.models import Equipamento
import qrcode
import os
import uuid as uuid_lib

class Command(BaseCommand):
    help = 'Gera QR codes para equipamentos com UUIDs válidos'

    def add_arguments(self, parser):
        parser.add_argument('--todos', action='store_true', help='Gerar para todos')
        parser.add_argument('--verificar', action='store_true', help='Apenas verificar UUIDs')

    def handle(self, *args, **options):
        bot_username = 'Mandacarusmbot'
        
        self.stdout.write("🤖 GERANDO QR CODES - MANDACARU BOT")
        self.stdout.write("=" * 50)
        
        # Verificar UUIDs primeiro
        if options['verificar']:
            self._verificar_uuids()
            return
        
        # Corrigir UUIDs se necessário
        self._corrigir_uuids()
        
        # Filtrar equipamentos
        if options['todos']:
            equipamentos = Equipamento.objects.all()
        else:
            equipamentos = Equipamento.objects.filter(ativo_nr12=True)

        total = equipamentos.count()
        self.stdout.write(f"\n🔄 Gerando QR codes para {total} equipamentos...")
        
        # Criar diretório
        pasta = os.path.join('media', 'qr_codes', 'equipamentos')
        os.makedirs(pasta, exist_ok=True)
        
        sucessos = 0

        for equipamento in equipamentos:
            try:
                # Verificar UUID
                if not equipamento.uuid:
                    self.stdout.write(f"❌ {equipamento.nome}: UUID nulo")
                    continue
                
                uuid_str = str(equipamento.uuid)
                if len(uuid_str) < 32:
                    self.stdout.write(f"❌ {equipamento.nome}: UUID inválido ({uuid_str})")
                    continue
                
                # Link para o bot
                qr_data = f"https://t.me/{bot_username}?start=eq_{uuid_str}"
                
                # Caminho do arquivo
                caminho_png = os.path.join(pasta, f"{uuid_str}.png")
                
                # Gerar QR Code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                img.save(caminho_png)
                
                self.stdout.write(f"✅ {equipamento.nome}")
                self.stdout.write(f"   UUID: {uuid_str}")
                self.stdout.write(f"   QR: {qr_data}")
                self.stdout.write(f"   Arquivo: {caminho_png}")
                self.stdout.write("")
                sucessos += 1
                
            except Exception as e:
                self.stdout.write(f"❌ Erro em {equipamento.nome}: {e}")

        self.stdout.write(self.style.SUCCESS(f"\n🎉 {sucessos} QR codes gerados com sucesso!"))
        self.stdout.write(f"📁 Pasta: {pasta}")
        
        # Mostrar exemplo de URL
        if sucessos > 0:
            primeiro_eq = equipamentos.first()
            exemplo_url = f"https://t.me/{bot_username}?start=eq_{primeiro_eq.uuid}"
            self.stdout.write(f"\n📱 Exemplo de URL: {exemplo_url}")

    def _verificar_uuids(self):
        """Verifica status dos UUIDs"""
        equipamentos = Equipamento.objects.all()
        validos = 0
        invalidos = 0
        
        for eq in equipamentos:
            if eq.uuid and len(str(eq.uuid)) >= 32:
                validos += 1
                self.stdout.write(f"✅ {eq.nome}: {eq.uuid}")
            else:
                invalidos += 1
                self.stdout.write(f"❌ {eq.nome}: UUID inválido ({eq.uuid})")
        
        self.stdout.write(f"\n📊 RESUMO: {validos} válidos, {invalidos} inválidos")

    def _corrigir_uuids(self):
        """Corrige UUIDs inválidos"""
        equipamentos = Equipamento.objects.all()
        corrigidos = 0
        
        for eq in equipamentos:
            if not eq.uuid or len(str(eq.uuid)) < 32:
                novo_uuid = uuid_lib.uuid4()
                eq.uuid = novo_uuid
                eq.save()
                self.stdout.write(f"🔧 {eq.nome}: UUID corrigido para {novo_uuid}")
                corrigidos += 1
        
        if corrigidos > 0:
            self.stdout.write(f"✅ {corrigidos} UUIDs corrigidos!")
        else:
            self.stdout.write("✅ Todos os UUIDs já são válidos!")