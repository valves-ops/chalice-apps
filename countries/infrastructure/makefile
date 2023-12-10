plan-dev:
	terraform plan -var-file=./environments/dev.tfvars -out=./.terraform/dev.tfplan 

apply-dev:
	terraform apply ./.terraform/dev.tfplan

plan-prod:
	terraform plan -var-file=./environments/prod.tfvars -out=./.terraform/prod.tfplan 

apply-prod:
	terraform apply ./.terraform/prod.tfplan 