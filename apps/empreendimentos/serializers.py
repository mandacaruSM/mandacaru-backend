class EmpreendimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empreendimento
        fields = '__all__'
