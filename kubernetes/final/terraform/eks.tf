module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.3"

  cluster_name    = local.cluster_name
  cluster_version = "1.27"

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  eks_managed_node_group_defaults = {
    ami_type = "AL2_x86_64"
  }

  eks_managed_node_groups = {
    group1 = {
      name = "prod-group"

      instance_types = ["t2.medium"]

      min_size     = 1
      max_size     = 3
      desired_size = 1
    },
    group2 = {
      name = "dev-group"

      instance_types = ["t2.medium"]

      min_size     = 1
      max_size     = 3
      desired_size = 1
    }
  }
}
