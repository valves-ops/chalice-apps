resource "aws_s3_bucket" "codepipeline_artifact_store" {
  bucket = "chalice-app-pipeline-artifact-store"
}

resource "aws_s3_object" "chalice_deployed_state" {
    bucket = "${aws_s3_bucket.codepipeline_artifact_store.id}"
    acl    = "private"
    key    = "chalice-deployed-state/"
    source = "/dev/null"
}