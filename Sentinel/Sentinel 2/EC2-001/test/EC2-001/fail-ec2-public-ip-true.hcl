module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-fail-ec2-public-ip-true.sentinel"
  }
}

test {
    rules = {
        main = false
    }
}
