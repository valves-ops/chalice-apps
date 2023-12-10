resource "aws_s3_bucket" "codepipeline_artifact_store" {
  bucket = "chalice-app-pipeline-artifact-store"
}