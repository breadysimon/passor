kubectl run caseviewer --replicas=2 --image=10.1.5.117:5000/caseviewer
kubectl expose deployment caseviewer --name=caseviewer --port=80  --type=LoadBalancer