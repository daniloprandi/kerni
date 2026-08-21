SSH Node Registration

Commands used to allow kerni-node to connect automatically to a node through SSH.

1. Check or create the SSH key

ssh-keygen -t ed25519

Creates an ED25519 SSH key pair for the current user. If the key already exists, do not overwrite it unless you intentionally want to replace it.

2. Copy the public key to the remote node

ssh-copy-id dprandi@192.168.200.133

Copies the public SSH key from kerni-node to the remote node. The remote password is entered once during this step.

3. Test passwordless SSH access

ssh 192.168.200.133 hostname

Connects to the remote node and executes hostname. If configured correctly, it returns the hostname without asking for a password.