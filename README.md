# Hooks

This is a simple web server that enables you to execute commands when you
receive web hooks from Github. This lets you, for example, redeploy things when
you push a commit.

## Installation

`pip install ghhooks` will do the trick, or just `sudo python ./setup.py
install`. Hooks depends on Flask.

## Deployment

### Stupid way

Just run `ghhooks` and it'll work well enough.

### Smart way

Install gunicorn and run `gunicorn hooks:app`, then set up a web server like
nginx to proxy to it (see [nginx](#nginx)). Use an init script from the init
directory, or write your own and send a pull request adding it.

## Configuration

It looks for `config.ini` in the CWD or uses `/etc/hooks.conf` if that doesn't
exist. An example is given in this repository as "config.ini":

    [example-hook]
    repository=SirCmpwn/hook
    branch=master
    command=echo Hello world!
    valid_ips=204.232.175.64/27,192.30.252.0/22,127.0.0.1
    # Note: these IP blocks are Github's hook servers, plus localhost

You may add as many hooks as you like, named by the `[example-hook]` line.

Hooks will pass Github's JSON payload into your hook command.

### Github configuration

1. Go to https://github.com/OWNER/REPOSITORY/settings/hooks/new (modify this
   URL as appropriate)
2. Set your payload URL to "http://your-server/hook"
3. Set the content type to `application/json`
4. Do not include a secret
5. "Just the `push` event"
6. Click "Add webhook" and you're good to go!

## Nginx

I suggest you run this behind nginx. The location configuration might look
something like this:

    location /hook {
        proxy_pass http://localhost:8000;
    }
