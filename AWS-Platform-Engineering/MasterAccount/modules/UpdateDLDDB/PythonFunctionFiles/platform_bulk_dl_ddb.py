import json, io, boto3, logging, os, urllib.parse
import pandas as pd
import simplejson as sj

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


class ExcelHandler(object):
  """
  # Class: Excel Handler
  # Description: Converts excel data to JSON and push to DynamoDB Table
  """

  def __init__(self, event, context):
    try:
      self.event = event
      self.context = context
      LOGGER.info("Event: %s" % self.event)
      LOGGER.info("Context: %s" % self.context)
      self.s3 = boto3.client('s3')
      self.dynamoDb = boto3.resource('dynamodb')
      self.table = self.dynamoDb.Table(os.environ['DDB_TABLE_NAME'])

    except Exception as error:
      LOGGER.info(error)
      print(error)
      return error


  def convertExcelRowToJson(self, excel_data_df):
    """
    # Convert excel data to JSON array
    """

    json_list = []
    try:
      for ind in excel_data_df.index:
        # Formatting the DL email address
        final_dl = f"{excel_data_df['DL'][ind]}@shell.com"
        if final_dl == "nan@shell.com":
          print(f"Null Entry for index {ind} in newly uploaded Excel sheet")
          continue
        LOGGER.info(final_dl)
        json_struct = {
            'DLEmailId': final_dl,
            'IsUsed': False,
            'InProgress': False
        }
        json_list.append(json_struct)

      # Serializing the JSON list to JSON array
      json_array = sj.dumps(json_list, ignore_nan=True, encoding="utf-8")
      LOGGER.info(json_array)
      return json_array

    except Exception as e:
      print(e.response['Error']['Message'])


  def pushDataToTable(self, json_array):
    """
    # Push JSON data to DynamoDB table
    """
    try:
      dl_data = json.loads(json_array)
      with self.table.batch_writer(overwrite_by_pkeys=['DLEmailId']) as batch:
        for item in dl_data:
          batch.put_item(Item=item)

    except Exception as e:
      print(e.response['Error']['Message'])


def lambda_handler(event, context):
  """
  # Lambda handler function to handle the S3 event
  """

  try:
    bucket = event['Records'][0]['s3']['bucket']['name']
    LOGGER.info("BUCKET : %s", bucket)
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    LOGGER.info("KEY : %s", key)

    excel_handler = ExcelHandler(event, context)

    response = excel_handler.s3.get_object(Bucket=bucket, Key=key)
    excel_data_df = pd.read_excel(io.BytesIO(response['Body'].read()), dtype=str)
    LOGGER.info(excel_data_df)
    json_array = excel_handler.convertExcelRowToJson(excel_data_df)
    excel_handler.pushDataToTable(json_array)
    return "Data has been inserted!!"

  except Exception as e:
    LOGGER.error("Update Bulk DDB Lambda has failed: '{0}'".format(e))
    return event