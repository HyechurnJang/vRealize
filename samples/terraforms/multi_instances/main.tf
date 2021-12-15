provider "aws" {
	version	= "2.69.0"
	region	= "ap-northeast-2"
}

resource "aws_instance" "vm1" {
	ami					= "ami-04876f29fd3a5e8ba"
	instance_type		= var.flavor
	availability_zone	= "ap-northeast-2a"
	subnet_id			= "subnet-02043a181981f40aa"
}

resource "aws_instance" "vm2" {
	ami					= "ami-04876f29fd3a5e8ba"
	instance_type		= var.flavor
	availability_zone	= "ap-northeast-2a"
	subnet_id			= "subnet-02043a181981f40aa"
}
