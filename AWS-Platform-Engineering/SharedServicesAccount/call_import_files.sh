regions=("us-east-1" "ap-southeast-1" "eu-west-1")

for region in "${regions[@]}"; do
  echo Calling for region -  $region
  output = ${aws ec2 describe-subnets --region $region}
  element=${echo "$output" | jq '.Subnets'}

done


