def aws_iam_check_if_analyzer_enabled(analyzer, analyzerName):
    try:
        response = analyzer.get_analyzer(
                        analyzerName=analyzerName
                    )
        print(response['analyzer'])
    except Exception as e:
        print("error occured while aws_iam_check_if_analyzer_enabled and error is {}".format(e))
        return False
    else:
         return True