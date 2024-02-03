terraform {
  backend "s3" {
    bucket         = "thesis-terraform"           
    key            = "terraform-version/terraform.tfstate"  
    region         = "ap-northeast-2"                  
    encrypt        = true                         
  }
}
