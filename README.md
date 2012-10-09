# adipasquale.github.com

## Web Resume

This page contains up-to-date infos on my previous experiences and what I'm currently doing.


## Why build this text-database-like script ?!

I wanted to completely separate my content and my presentation, but without a classic database, that seems
way overkill for such a simple, static pages website.

I couldn't find any decent solution on the web so I decided to just go for it and write a small script. And heck, it never hurts to write some python and regexes.


## Useful commands

This will start the custom build watch process (execute from directory root)

```shell
sass --watch . -r ./bourbon/lib/bourbon.rb
```


You have to explicitly include bourbon when you launch SASS watch process

```shell
cd css
sass --watch . -r ./bourbon/lib/bourbon.rb
```