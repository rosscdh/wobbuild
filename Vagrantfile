# Optimized for Vagrant 1.7 and above.
Vagrant.require_version ">= 1.7.0"

Vagrant.configure(2) do |config|

  config.vm.box = "centos/7"

  config.vm.provider "virtualbox" do |v|
    host = RbConfig::CONFIG['host_os']

    # Give VM 1/4 system memory 
    if host =~ /darwin/
      # sysctl returns Bytes and we need to convert to MB
      mem = `sysctl -n hw.memsize`.to_i / 1024
    elsif host =~ /linux/
      # meminfo shows KB and we need to convert to MB
      mem = `grep 'MemTotal' /proc/meminfo | sed -e 's/MemTotal://' -e 's/ kB//'`.to_i 
    elsif host =~ /mswin|mingw|cygwin/
      # Windows code via https://github.com/rdsubhas/vagrant-faster
      mem = `wmic computersystem Get TotalPhysicalMemory`.split[1].to_i / 1024
    end

    mem = mem / 1024 / 4
    v.customize ["modifyvm", :id, "--memory", mem]

    # v.memory = 1024
  end

  # Disable the new default behavior introduced in Vagrant 1.7, to
  # ensure that all Vagrant machines will use the same SSH key pair.
  # See https://github.com/mitchellh/vagrant/issues/5005
  config.ssh.insert_key = false

  # config.vm.provision :shell, privileged: false do |s|
  #   s.inline = <<-SHELL
  #      echo -e \"#{File.read("#{Dir.home}/.gitconfig")}\" > /home/vagrant/.gitconfig
  #   SHELL
  # end

  config.vm.provision :shell, privileged: false do |s|
    ssh_pub_key = File.readlines("#{Dir.home}/.ssh/id_rsa.pub").first.strip
    s.inline = <<-SHELL
       echo #{ssh_pub_key} >> /home/vagrant/.ssh/authorized_keys
    SHELL
  end  

  config.vm.provision "ansible" do |ansible|
    ansible.verbose = "vv"
    ansible.playbook = "playbooks/vagrant.yml"
    ansible.extra_vars = {
    }
  end

  config.vm.network "forwarded_port", guest: 8280, host: 8280  
  config.vm.network "private_network", ip: "192.168.50.5"
  config.ssh.forward_agent    = true

  config.vm.synced_folder '.', '/vagrant', nfs: true

end