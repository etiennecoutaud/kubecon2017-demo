# kubecon2017-demo
This project contain ressources for demo during the North America kubecon2017

Requirements
============
To use this code you need to have :
- Vagrant >= 1.9.7
- VirtualBox >= 5.1.30
- Ansible >= 2.4

Setup infrastructure
====================
Vagrant will bootrsap an architecture with 3 vms:
- App vm
- Kafka vm
- Prometheus vm

To build it:
```
$ cd infra
$ vagrant up
$ ansible-playbook -i inventories/vagrant.ini install.yml
```
