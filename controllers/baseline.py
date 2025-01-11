import json

from schemas import baseline_schema
from factories import embeddings_factory, llm_factory

def start(args):
    with open(args.filename, 'r') as file:
        data = json.load(file)
        
    baseline_schema.validate(data)

    llm_service = llm_factory.getLLM(args.query_llm)
    query_model = args.query_model

    llm_supported_model = llm_service.validateModel(query_model)

    if llm_supported_model == False:
        raise TypeError(f"{args.query_model} is not a valid query model for {args.query_llm}")
    
    embeddings_service = embeddings_factory.getEmbeddings(args.embeddings_llm)
    embeddings_model = args.embeddings_model

    embeddings_supported_model = embeddings_service.validateEmbeddings(embeddings_model)

    if embeddings_supported_model == False:
        raise TypeError(f"{args.embeddings_model} is not a valid embeddings model for {args.embeddings_llm}")
    
    baseline_data = _generate_baseline(llm_service, query_model, embeddings_service, embeddings_model, data)

    _output_baseline(llm_service, embeddings_service, query_model, embeddings_model, baseline_data)

def _generate_baseline(llm_service, embeddings_service, query_model, embeddings_model, data):
    baseline_data = []

    for query in data:
        llm_response = llm_service.query(query_model, query)
        response_embeddings = embeddings_service.embed(embeddings_model, llm_response)

        baseline_data.append({
          {
            "query": query,
            "response": llm_response,
            "vector": response_embeddings
          }
        })
    
    return baseline_data

def _output_baseline(ll_service, embeddings_service, baseline, file):
    with open(file, "w") as file:
        json.dump({
          "llm": {
              "source": ll_service.get_source(),
              "model": ll_service.get_model()
          },
          "embeddings": {
              "source": embeddings_service.get_source(),
              "model": embeddings_service.get_model()
          },
          "data": baseline
        }, file, indent=4)