from datetime import datetime, timedelta, timezone
import oci
import sys

def get_metric_data(region, compartment_id, namespace, metric_name, resource_id):
    config = oci.config.from_file()
    config['region'] = region

    monitoring_client = oci.monitoring.MonitoringClient(config)

    # Construir a consulta com os filtros de dimensão
    if metric_name in ["GetMessagesFault.Count", "GetMessagesSuccess.Count","PutMessagesRecords.Count","PutMessagesSuccess.Count","PutMessagesFault.Count"]:
        query = f'{metric_name}[1m]{{region = "{region}", resourceId = "{resource_id}"}}.sum()'
    elif metric_name in ["GetMessagesLatency.Time","PutMessagesLatency.Time","GetMessagesThroughput.Bytes", "PutMessagesThroughput.Bytes"]:
        query = f'{metric_name}[1m]{{region = "{region}", resourceId = "{resource_id}"}}.avg()'
    
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=5)

    # Enviar a solicitação ao serviço
    summarize_metrics_data_response = monitoring_client.summarize_metrics_data(
        compartment_id=compartment_id,
        summarize_metrics_data_details=oci.monitoring.models.SummarizeMetricsDataDetails(
            namespace=namespace,
            query=query,        
            start_time=start_time,
            end_time=end_time,
            resolution="5m"),
        compartment_id_in_subtree=False)
    
    # Obter os dados da resposta
    metric_data_list = summarize_metrics_data_response.data

    # Acessar os aggregated_datapoints
    if metric_data_list:
        aggregated_datapoints = metric_data_list[0].aggregated_datapoints
        latest_datapoint = max(aggregated_datapoints, key=lambda x: x.timestamp)
        latest_value = latest_datapoint.value
        print(latest_value)
    else:
        print("0.0")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py region compartment_id metric_name resource_id")
        sys.exit(1)

    region = sys.argv[1]
    compartment_id = sys.argv[2]
    namespace = "oci_streaming"
    metric_name = sys.argv[3]
    resource_id = sys.argv[4]

    get_metric_data(region, compartment_id, namespace, metric_name, resource_id)
