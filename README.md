Projeto - Módulo 1: Implementar Análise de Sentimentos em Avaliações de Produtos

- Coletar avaliações de um produto selecionado: texto e nota
- Treinar classificador: SVM + bow, SVM + embeddings, BERT
- Bônus: utilizar in-context learning para a classificação

Apresentação reportando resultados (F1 e acurácia) e análises (notebook)


Detalhes: 

- Quero que utilize as avaliações do filme O Agente Secreto no site do IMDB (https://www.imdb.com/pt/title/tt27847051/reviews/?ref_=ttrt_sa_3)
- Crie uma visualização UI para demonstrar os resultados solicitados
- Quero que crie uma versão do projeto para rodar em um notebook (.ipynb)

Considerações sobre resultados iniciais da base:

Com 104 reviews (83 treino, 21 teste) e classes desbalanceadas (51 Positivo vs 16 Neutro vs 16 Negativo no treino), os resultados são esperados. Principais problemas e estratégias: 

Diagnóstico

1. Dataset muito pequeno — 83 amostras de treino é pouco para fine-tuning de BERT (110M parâmetros)   
2. Desbalanceamento — Positivo tem 3x mais amostras que as outras classes                             
3. Texto pré-processado — BERT funciona melhor com texto original (ele tem seu próprio tokenizer)

Estratégias de Melhoria                                                                               

Dados:                                                                                                
- Aumentar o dataset com reviews de outros filmes similares (data augmentation)                       
- Usar o texto original (não o text_clean) no BERT — ele já lida com capitalização e pontuação

Desbalanceamento:

- Class weights no loss (penalizar mais erros nas classes minoritárias)
- Oversampling das classes Negativo/Neutro

Modelo:
- Usar validação cruzada (StratifiedKFold) ao invés de um único split, dado o tamanho pequeno
- Ajustar hiperparâmetros (learning rate, epochs, warmup)
- Congelar camadas iniciais do BERT e só treinar as finais (menos overfitting)

Avaliação:
- Com 21 amostras de teste (4 Negativo, 4 Neutro, 13 Positivo), uma única predição errada muda muito  
  as métricas
  
Quer que eu implemente alguma dessas melhorias no notebook? A mais impactante seria combinar: usar    
  texto original + class weights + cross-validation.