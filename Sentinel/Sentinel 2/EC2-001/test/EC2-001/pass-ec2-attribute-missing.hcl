module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-pass-ec2-attribute-missing.sentinel"
  }
}

test {
    rules = {
        main = true
    }
}
