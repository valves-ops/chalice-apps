resource "aws_codepipeline" "chalice_pipeline" {
  name     = "chalice-pipeline"
  role_arn = aws_iam_role.pipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.codepipeline_artifact_store.bucket
    type     = "S3"
  }
  # Source
  stage {
    name = "Source"

    action {
      category         = "Source"
      name             = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        ConnectionArn    = "arn:aws:codestar-connections:sa-east-1:048689258641:connection/78c1b580-ec13-4e80-913f-ed95cb7d1339"
        FullRepositoryId = "valves-ops/chalice-apps"
        BranchName       = "main"
        DetectChanges    = true
        OutputArtifactFormat = "CODEBUILD_CLONE_REF" # ensures git metadata will be present
      }
    }
  }

  # Test
  stage {
    name = "Test"
    action {
      category  = "Build"
      name      = "Build"
      owner     = "AWS"
      provider  = "CodeBuild"
      version   = "1"
      run_order = 1
      input_artifacts  = ["source_output"]

      configuration = {
        ProjectName = aws_codebuild_project.test_job.name
      }
    }
  }

  # Deploy
  stage {
    name = "Deploy"
    action {
      category  = "Build"
      name      = "Build"
      owner     = "AWS"
      provider  = "CodeBuild"
      version   = "1"
      run_order = 1
      input_artifacts  = ["source_output"]

      configuration = {
        ProjectName = aws_codebuild_project.deploy_job.name
      }
    }
  }
}