resource "aws_ssm_document" "platform_windows_document_public" {
  count           =  var.Connectivity == "PUB" ? 1 : 0

  name            = "platform_windows_document"
  document_format = "YAML"
  document_type   = "Command"
  target_type     = "/AWS::EC2::Instance"
  tags = {
    platform_donotdelete = "yes"
  }

  content       =  file("${path.module}/platform_windows_public.yaml")
}

resource "aws_ssm_document" "platform_windows_document_private" {
  count           =  var.Connectivity == "PVT" ? 1 : 0

  name            = "platform_windows_document"
  document_format = "YAML"
  document_type   = "Command"
  target_type     = "/AWS::EC2::Instance"
  tags = {
    platform_donotdelete = "yes"
  }

  content       = file("${path.module}/platform_windows_private.yaml")
}

resource "aws_ssm_document" "platform_linux_document_public" {
  count           =  var.Connectivity == "PUB" ? 1 : 0

  name            = "platform_Linux_document"
  document_format = "YAML"
  document_type   = "Command"
  target_type     = "/AWS::EC2::Instance"
  tags = {
    platform_donotdelete = "yes"
  }

  content       = file("${path.module}/platform_linux_public.yaml")
}

resource "aws_ssm_document" "platform_linux_document_private" {
  count           =  var.Connectivity == "PVT" ? 1 : 0

  name            = "platform_Linux_document"
  document_format = "YAML"
  document_type   = "Command"
  target_type     = "/AWS::EC2::Instance"
  tags = {
    platform_donotdelete = "yes"
  }

  content       = file("${path.module}/platform_linux_private.yaml")
}

resource "aws_ssm_association" "platform_windows_document_public_association" {
    count               =  var.Connectivity == "PUB" ? 1 : 0

    name                = "platform_windows_document"
    schedule_expression = "rate(240 minutes)"
    document_version    = aws_ssm_document.platform_windows_document_public[0].latest_version
    parameters = {
                  cloudWatchAction = "configure"
                  mode = "ec2"
                  optionalConfigurationSource = "ssm"
                  optionalConfigurationLocationWindows = "platform_AmazonCloudWatch-windows"
                  optionalRestart ="yes"
                  action = "Install"
                  installationType = "Uninstall and reinstall"
                  name = "AmazonCloudWatchAgent"
                  version = "latest"
                  executionTimeout = var.SSMParameters.platform_execution_timeout
                  sourceType = "S3"
                  commandLineForRapidWindows = var.SSMParameters.platform_rapid7_win_filename
                  commandLineForCloudhealthWindows = var.SSMParameters.platform_ch_win_filename
                  commandLineForFalconWindows = var.SSMParameters.platform_falcon_win_filename
                  commandLineForFlexeraWindows = var.SSMParameters.platform_flexera_win_filename
                  sourceInfoForRapidWindows = jsonencode({path = replace(var.SSMParameters.platform_pub_rapid7_winpath , "\"", "")})
                  sourceInfoForFlexeraWindows = jsonencode({path = replace(var.SSMParameters.platform_pub_flexera_winpath, "\"","")})
                  sourceInfoForFalconWindows = jsonencode({path = replace(var.SSMParameters.platform_pub_falcon_winpath, "\"", "")})
                  sourceInfoForCloudhealthWindows = jsonencode({path = replace(var.SSMParameters.platform_pub_ch_winpath,"\"", "")})
                  workingDirectoryWindows = var.SSMParameters.platform_win_dirpath
              }
    targets {
      key    = "tag:platform_windows_association"
      values = ["yes"]
    }
    association_name = "platform_Windows_association"
}

resource "aws_ssm_association" "platform_windows_document_private_association_us" {
    count               =  data.aws_region.current.name == "us-east-1" && var.Connectivity == "PVT" ? 1 : 0

    name                = "platform_windows_document"
    schedule_expression = "rate(240 minutes)"
    document_version    = aws_ssm_document.platform_windows_document_private[0].latest_version
    parameters = {
                  cloudWatchAction = "configure"
                  mode = "ec2"
                  optionalConfigurationSource = "ssm"
                  optionalConfigurationLocationWindows = "platform_AmazonCloudWatch-windows"
                  optionalRestart = "yes"
                  action = "Install"
                  installationType = "Uninstall and reinstall"
                  name = "AmazonCloudWatchAgent"
                  version = "latest"
                  executionTimeout = var.SSMParameters.platform_execution_timeout
                  sourceType = "S3"
                  commandLineForRapidWindows = var.SSMParameters.platform_rapid7_win_filename
                  commandLineForCloudhealthWindows = var.SSMParameters.platform_ch_win_filename
                  commandLineForFalconWindows = var.SSMParameters.platform_falcon_win_filename
                  commandLineForFlexeraWindows = var.SSMParameters.platform_flexera_win_filename
                  sourceInfoForRapidWindows = jsonencode({path = replace(var.SSMParameters.platform_pvt_rapid7_winpath , "\"","")})
                  sourceInfoForFlexeraWindows = jsonencode({path = replace(var.SSMParameters.platform_pvt_flexera_winpath_us, "\"", "")})
                  sourceInfoForFalconWindows = jsonencode({path = replace(var.SSMParameters.platform_pvt_falcon_winpath, "\"", "")})
                  sourceInfoForCloudhealthWindows = jsonencode({path = replace(var.SSMParameters.platform_pvt_ch_winpath, "\"", "")})
                  workingDirectoryWindows = var.SSMParameters.platform_win_dirpath
                  sourceInfoForWindows = jsonencode({path = replace(var.SSMParameters.domainjoin_windowsURL_us,"\"", "")})
                  commandLineForWindows = var.SSMParameters.domainjoin_windows_filename
                  workingDirectoryForWindowsDomainJoin = var.SSMParameters.domainjoin_windows_path
              }
    targets {
      key    = "tag:platform_windows_association"
      values = ["yes"]
    }
    association_name = "platform_Windows_association"
}

resource "aws_ssm_association" "platform_windows_document_private_association_eu" {
    count               =  data.aws_region.current.name == "eu-west-1" && var.Connectivity == "PVT" ? 1 : 0

    name                = "platform_windows_document"
    schedule_expression = "rate(240 minutes)"
    document_version    = aws_ssm_document.platform_windows_document_private[0].latest_version
    parameters = {
                  cloudWatchAction = "configure"
                  mode = "ec2"
                  optionalConfigurationSource = "ssm"
                  optionalConfigurationLocationWindows = "platform_AmazonCloudWatch-windows"
                  optionalRestart = "yes"
                  action = "Install"
                  installationType = "Uninstall and reinstall"
                  name = "AmazonCloudWatchAgent"
                  version = "latest"
                  executionTimeout = var.SSMParameters.platform_execution_timeout
                  sourceType = "S3"
                  commandLineForRapidWindows = var.SSMParameters.platform_rapid7_win_filename
                  commandLineForCloudhealthWindows = var.SSMParameters.platform_ch_win_filename
                  commandLineForFalconWindows = var.SSMParameters.platform_falcon_win_filename
                  commandLineForFlexeraWindows = var.SSMParameters.platform_flexera_win_filename
                  sourceInfoForRapidWindows = jsonencode({path = replace(var.SSMParameters.platform_pvt_rapid7_winpath , "\"","")})
                  sourceInfoForFlexeraWindows = jsonencode({path = replace(var.SSMParameters.platform_pvt_flexera_winpath_eu, "\"", "")})
                  sourceInfoForFalconWindows = jsonencode({path = replace(var.SSMParameters.platform_pvt_falcon_winpath, "\"", "")})
                  sourceInfoForCloudhealthWindows = jsonencode({path = replace(var.SSMParameters.platform_pvt_ch_winpath, "\"", "")})
                  workingDirectoryWindows = var.SSMParameters.platform_win_dirpath
                  sourceInfoForWindows = jsonencode({path = replace(var.SSMParameters.domainjoin_windowsURL_eu,"\"", "")})
                  commandLineForWindows = var.SSMParameters.domainjoin_windows_filename
                  workingDirectoryForWindowsDomainJoin = var.SSMParameters.domainjoin_windows_path
              }
    targets {
      key    = "tag:platform_windows_association"
      values = ["yes"]
    }
    association_name = "platform_Windows_association"
}

resource "aws_ssm_association" "platform_windows_document_private_association_sg" {
    count               =  data.aws_region.current.name == "ap-southeast-1" && var.Connectivity == "PVT" ? 1 : 0

    name                = "platform_windows_document"
    schedule_expression = "rate(240 minutes)"
    document_version    = aws_ssm_document.platform_windows_document_private[0].latest_version
    parameters = {
                  cloudWatchAction = "configure"
                  mode = "ec2"
                  optionalConfigurationSource = "ssm"
                  optionalConfigurationLocationWindows = "platform_AmazonCloudWatch-windows"
                  optionalRestart = "yes"
                  action = "Install"
                  installationType = "Uninstall and reinstall"
                  name = "AmazonCloudWatchAgent"
                  version = "latest"
                  executionTimeout = var.SSMParameters.platform_execution_timeout
                  sourceType = "S3"
                  commandLineForRapidWindows = var.SSMParameters.platform_rapid7_win_filename
                  commandLineForCloudhealthWindows = var.SSMParameters.platform_ch_win_filename
                  commandLineForFalconWindows = var.SSMParameters.platform_falcon_win_filename
                  commandLineForFlexeraWindows = var.SSMParameters.platform_flexera_win_filename
                  sourceInfoForRapidWindows = jsonencode({path = replace(var.SSMParameters.platform_pvt_rapid7_winpath , "\"","")})
                  sourceInfoForFlexeraWindows = jsonencode({path = replace(var.SSMParameters.platform_pvt_flexera_winpath_sg, "\"", "")})
                  sourceInfoForFalconWindows = jsonencode({path = replace(var.SSMParameters.platform_pvt_falcon_winpath, "\"", "")})
                  sourceInfoForCloudhealthWindows = jsonencode({path = replace(var.SSMParameters.platform_pvt_ch_winpath, "\"", "")})
                  workingDirectoryWindows = var.SSMParameters.platform_win_dirpath
                  sourceInfoForWindows = jsonencode({path = replace(var.SSMParameters.domainjoin_windowsURL_sg,"\"", "")})
                  commandLineForWindows = var.SSMParameters.domainjoin_windows_filename
                  workingDirectoryForWindowsDomainJoin = var.SSMParameters.domainjoin_windows_path
              }
    targets {
      key    = "tag:platform_windows_association"
      values = ["yes"]
    }
    association_name = "platform_Windows_association"
}

resource "aws_ssm_association" "platform_linux_document_public_association" {
    count               =  var.Connectivity == "PUB" ? 1 : 0

    name                = "platform_Linux_document"
    schedule_expression = "rate(240 minutes)"
    document_version    = aws_ssm_document.platform_linux_document_public[0].latest_version
    parameters = {
                  cloudWatchAction = "configure"
                  mode = "ec2"
                  optionalConfigurationSource = "ssm"
                  optionalConfigurationLocationLinux = "platform_AmazonCloudWatch-Linux"
                  optionalRestart = "yes"
                  action = "Install"
                  installationType = "Uninstall and reinstall"
                  name = "AmazonCloudWatchAgent"
                  version = "latest"
                  commandLineForRapidLinux = var.SSMParameters.platform_rapid7_linux_filename
                  commandLineForCloudHealthLinux = var.SSMParameters.platform_ch_linux_filename
                  commandLineForFalconLinux = var.SSMParameters.platform_falcon_linux_filename
                  commandLineForFlexeraLinux = var.SSMParameters.platform_flexera_linux_filename
                  executionTimeout = var.SSMParameters.platform_execution_timeout
                  sourceInfoForRapidLinux = jsonencode({path = replace(var.SSMParameters.platform_pub_rapid7_linuxpath , "\"","")})
                  sourceInfoForFlexeraLinux = jsonencode({path = replace(var.SSMParameters.platform_pub_flexera_linuxpath, "\"", "")})
                  sourceInfoForFalconLinux = jsonencode({path = replace(var.SSMParameters.platform_pub_falcon_linuxpath, "\"", "")})
                  sourceInfoForCloudhealthLinux = jsonencode({path = replace(var.SSMParameters.platform_pub_ch_linuxpath, "\"", "")})
                  sourceType = "S3"
                  workingDirectoryLinux = var.SSMParameters.platform_linux_dirpath
              }
    targets {
      key    = "tag:platform_linux_association"
      values = ["yes"]
    }
    association_name = "platform_Windows_association"
}

resource "aws_ssm_association" "platform_linux_document_private_association_us" {
    count               =  data.aws_region.current.name == "us-east-1" && var.Connectivity == "PVT" ? 1 : 0

    name                = "platform_Linux_document"
    schedule_expression = "rate(240 minutes)"
    document_version    = aws_ssm_document.platform_linux_document_private[0].latest_version
    parameters = {
                  cloudWatchAction = "configure"
                  mode = "ec2"
                  optionalConfigurationSource = "ssm"
                  optionalConfigurationLocationLinux = "platform_AmazonCloudWatch-Linux"
                  optionalRestart = "yes"
                  action = "Install"
                  installationType = "Uninstall and reinstall"
                  name = "AmazonCloudWatchAgent"
                  version = "latest"
                  commandLineForRapidLinux = var.SSMParameters.platform_rapid7_linux_filename
                  commandLineForCloudHealthLinux = var.SSMParameters.platform_ch_linux_filename
                  commandLineForFalconLinux = var.SSMParameters.platform_falcon_linux_filename
                  commandLineForFlexeraLinux = var.SSMParameters.platform_flexera_linux_filename
                  executionTimeout = var.SSMParameters.platform_execution_timeout
                  sourceInfoForRapidLinux = jsonencode({path = replace(var.SSMParameters.platform_pvt_rapid7_linuxpath , "\"", "")})
                  sourceInfoForFlexeraLinux = jsonencode({path = replace(var.SSMParameters.platform_pvt_flexera_linuxpath_us, "\"","")})
                  sourceInfoForFalconLinux = jsonencode({path = replace(var.SSMParameters.platform_pvt_falcon_linuxpath, "\"", "")})
                  sourceInfoForCloudhealthLinux = jsonencode({path = replace(var.SSMParameters.platform_pvt_ch_linuxpath, "\"", "")})
                  sourceType = "S3"
                  workingDirectoryLinux = var.SSMParameters.platform_linux_dirpath
                  sourceInfoForLinux = jsonencode({path = replace(var.SSMParameters.domainjoin_linuxmainURL,"\"", "")})
                  sourceInfoForPreLinux =jsonencode({path = replace(var.SSMParameters.domainjoin_linuxpreURL,"\"", "")})
                  commandLineForLinux = var.SSMParameters.domainjoin_linux_mainfilename
                  commandLineForPrelinux = var.SSMParameters.domainjoin_linuxpreURL
                  workingDirectoryForLinuxDomainJoin = var.SSMParameters.domainjoin_linuxpath
              }
    targets {
      key    = "tag:platform_linux_association"
      values = ["yes"]
    }
    association_name = "platform_Linux_association"
}

resource "aws_ssm_association" "platform_linux_document_private_association_eu" {
    count               =  data.aws_region.current.name == "eu-west-1" && var.Connectivity == "PVT" ? 1 : 0

    name                = "platform_Linux_document"
    schedule_expression = "rate(240 minutes)"
    document_version    = aws_ssm_document.platform_linux_document_private[0].latest_version
    parameters = {
                  cloudWatchAction = "configure"
                  mode = "ec2"
                  optionalConfigurationSource = "ssm"
                  optionalConfigurationLocationLinux = "platform_AmazonCloudWatch-Linux"
                  optionalRestart = "yes"
                  action = "Install"
                  installationType = "Uninstall and reinstall"
                  name = "AmazonCloudWatchAgent"
                  version = "latest"
                  commandLineForRapidLinux = var.SSMParameters.platform_rapid7_linux_filename
                  commandLineForCloudHealthLinux = var.SSMParameters.platform_ch_linux_filename
                  commandLineForFalconLinux = var.SSMParameters.platform_falcon_linux_filename
                  commandLineForFlexeraLinux = var.SSMParameters.platform_flexera_linux_filename
                  executionTimeout = var.SSMParameters.platform_execution_timeout
                  sourceInfoForRapidLinux = jsonencode({path = replace(var.SSMParameters.platform_pvt_rapid7_linuxpath , "\"", "")})
                  sourceInfoForFlexeraLinux = jsonencode({path = replace(var.SSMParameters.platform_pvt_flexera_linuxpath_eu, "\"","")})
                  sourceInfoForFalconLinux = jsonencode({path = replace(var.SSMParameters.platform_pvt_falcon_linuxpath, "\"", "")})
                  sourceInfoForCloudhealthLinux = jsonencode({path = replace(var.SSMParameters.platform_pvt_ch_linuxpath, "\"", "")})
                  sourceType = "S3"
                  workingDirectoryLinux = var.SSMParameters.platform_linux_dirpath
                  sourceInfoForLinux = jsonencode({path = replace(var.SSMParameters.domainjoin_linuxmainURL,"\"", "")})
                  sourceInfoForPreLinux = jsonencode({path = replace(var.SSMParameters.domainjoin_linuxpreURL,"\"", "")})
                  commandLineForLinux = var.SSMParameters.domainjoin_linux_mainfilename
                  commandLineForPrelinux = var.SSMParameters.domainjoin_linuxpreURL
                  workingDirectoryForLinuxDomainJoin = var.SSMParameters.domainjoin_linuxpath
              }
    targets {
      key    = "tag:platform_linux_association"
      values = ["yes"]
    }
    association_name = "platform_Linux_association"
}

resource "aws_ssm_association" "platform_linux_document_private_association_sg" {
    count               =  data.aws_region.current.name == "ap-southeast-1" && var.Connectivity == "PVT" ? 1 : 0

    name                = "platform_Linux_document"
    schedule_expression = "rate(240 minutes)"
    document_version    = aws_ssm_document.platform_linux_document_private[0].latest_version
    parameters = {
                  cloudWatchAction = "configure"
                  mode = "ec2"
                  optionalConfigurationSource = "ssm"
                  optionalConfigurationLocationLinux = "platform_AmazonCloudWatch-Linux"
                  optionalRestart = "yes"
                  action = "Install"
                  installationType = "Uninstall and reinstall"
                  name = "AmazonCloudWatchAgent"
                  version = "latest"
                  commandLineForRapidLinux = var.SSMParameters.platform_rapid7_linux_filename
                  commandLineForCloudHealthLinux = var.SSMParameters.platform_ch_linux_filename
                  commandLineForFalconLinux = var.SSMParameters.platform_falcon_linux_filename
                  commandLineForFlexeraLinux = var.SSMParameters.platform_flexera_linux_filename
                  executionTimeout = var.SSMParameters.platform_execution_timeout
                  sourceInfoForRapidLinux = jsonencode({path = replace(var.SSMParameters.platform_pvt_rapid7_linuxpath , "\"", "")})
                  sourceInfoForFlexeraLinux = jsonencode({path = replace(var.SSMParameters.platform_pvt_flexera_linuxpath_sg, "\"","")})
                  sourceInfoForFalconLinux = jsonencode({path = replace(var.SSMParameters.platform_pvt_falcon_linuxpath, "\"", "")})
                  sourceInfoForCloudhealthLinux = jsonencode({path = replace(var.SSMParameters.platform_pvt_ch_linuxpath, "\"", "")})
                  sourceType = "S3"
                  workingDirectoryLinux = var.SSMParameters.platform_linux_dirpath
                  sourceInfoForLinux = jsonencode({path = replace(var.SSMParameters.domainjoin_linuxmainURL,"\"", "")})
                  sourceInfoForPreLinux = jsonencode({path = replace(var.SSMParameters.domainjoin_linuxpreURL,"\"", "")})
                  commandLineForLinux = var.SSMParameters.domainjoin_linux_mainfilename
                  commandLineForPrelinux = var.SSMParameters.domainjoin_linuxpreURL
                  workingDirectoryForLinuxDomainJoin = var.SSMParameters.domainjoin_linuxpath
              }
    targets {
      key    = "tag:platform_linux_association"
      values = ["yes"]
    }
    association_name = "platform_Linux_association"
}