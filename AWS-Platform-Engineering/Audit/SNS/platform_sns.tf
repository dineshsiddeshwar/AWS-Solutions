data "aws_kms_key" "sharr_key"{
    key_id = "alias/SO0111-SHARR-Key" 
}


resource "aws_sns_topic" "SHARRTopic229CFB9E" {
  name = "SO0111-SHARR_Topic"
  display_name = "SHARR Playbook Topic (SO0111)"
  kms_master_key_id = data.aws_kms_key.sharr_key.arn
}

