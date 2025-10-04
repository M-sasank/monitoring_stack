# Migrating to K8s

during small workloads, many of us run the applciations using docker compose in a single Virtual Machine. This works on small loads, but as the project scales - we will suddenly be experiencing crashes, user complaints - which are some cues you should consider and migrate to a better deployment architecture like the Kubernetes.

The following will guide you how to properly do this while also explaining why we are doing, what we are doing. 

**Note: This guide should only be attempted when you are fairly comfortable with Kubernetes concepts, otherwise go watch some `KodeKloud` or `TechWorld with Nana` videos and come back :)**

## 1. Infrastructure 
Before we can migrate to a secure, production kubernetes deployment we need the following infra. 
### 1.1 Secure Networking (VPC, NAT Gateways, Firewall, Cloud Armor)
 This is the foundation. It include:
 - **VPC** to create an isolated network
 - **Private Cluster configurations** to prevent public exposure of nodes and the control plane
 - **Firewalls** 
 - **Cloud Armor (WAF)** to filter traffic, and NAT Gateways for secure outbound connections.
### 1.2. Network layer Ingress controler / Load Balancer
This is how traffic gets into your cluster. It involves:
- **Ingress Controller** that provisions a cloud Load Balancer, integrated with a WAF (like Cloud Armor) and automated SSL/TLS certificates for encryption
### 1.3.  Secure Software Supply Chain
This is how your code gets into the cluster. It includes:
- **Private Artifact Registry** to store and scan your container images
- **CI/CD pipeline** to automate the building, testing, and deployment of your code.
### 1.4. Observability Stack
- Metrics for performance monitoring and alerting (Prometheus/Cloud Monitoring).

- Logs for debugging and auditing (Loki/Cloud Logging).

- Traces for understanding request flows in a microservices architecture (Cloud Trace/Jaeger).

### 1.5. Identity & Access Management (IAM)
This is the security layer for permissions. It involves granting least-privilege roles to users, etc.

**You don't need to set these up right away, these are put here so you can learn basics of those you don't know before we proceed to next steps.** 

## 2. Setup CI/CD & Publish Artifacts
Kubernetes cannot build image, it will only pull images from a registry like GAR, Dockerhub Quay etc. You can build them manually and push to a registry or use CI/CD to do it automatically.

- **Optimize Dockerfiles:** Make sure your Dockerfiles are optimized for production (e.g., using multi-stage builds to create smaller, more secure images).

 - **Push to a Private Registry:** Instead of loading images into a local cluster, you must push them to a secure, private container registry. For a GKE deployment, the standard is Google's Artifact Registry. This gives you a central, versioned, and scanned location for your images.

 ## 3. Kubernetes configuration files


 ## 4. Provision Infrastructure with Terraform (optional)
 After you have created k8 configs and tested out locally. It's time to setup infrastructure. Without infra, you cannot deploy or automate deploy the files we created.

Refer this for indepth guides for terraform 

You can create the Infra manually or write IaC configs to manage and change them. The latter is recommended.

What you or your terraform code should create:

- A VPC and private subnets.

- Firewall Rules to control traffic.

- A GKE Private Cluster with appropriate node pools (e.g., a "regular-pool" and a "high-cpu-pool" with the correct machine types).

- The Artifact Registry repository to store your images.

- IAM Service Accounts for your nodes and, most importantly, for Workload Identity.

## 5. Test the cloud deployment


## 6. Complete CI/CD with automated k8 deployments
That's it! You have succesfully migrated things to k8s. 

---
# Optional ArgoCD setup
This is the modern, industry-standard way to deploy to Kubernetes. Instead of having your CI pipeline run kubectl apply, you use a GitOps tool.
