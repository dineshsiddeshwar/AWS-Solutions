# Azure Data Factory

This modules creates data factory resource with 'n' number of datasets, integration runtimes, linked services, pipeline and trigger schedule. Except self_hosted runtime.

> [!NOTE]
> Datasets and linked services are created in pairs, so you will have to pass in a map of object for each dataset/ linked service pair that you want to create. Refer to the terraform documentation to know the parameters that each dataset/ linked service require/ accept.

**An example of of to use this module.**

```terraform
module "data_factory" {
  source = "../Modules/Data_factory_module"
  resource_group_name = "EYGDSSECbaseline-rg"
  df_name = "eygdssec-data-factory"
  dataset_azure_blob = {
    blob_data_set_1 = {
      dataset_name = "testdatasetblob"
      connection_string = "DefaultEndpointsProtocol=https;AccountName=eygdsbaseline;AccountKey=354LYEqSk5H3chbTQYkCHukuUgFhPoSnrhKY5Y3HZz+FNJovi3r4AHNRtaAkHMVbQmFIFF9dCVt+6TnaigwqRg==;EndpointSuffix=core.windows.net"
    }
  }
}
```


