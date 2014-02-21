# Fnitter

Projekt för att ta skärmdumpar av folks twitter-konton. 

Det är uppdelat i flera komponenter. 

## PhantomJS skript (färdigt)

I tools/screenshot.js finns ett skript som tar skärmdumpar av webbsidor med PhantomJS. 

## Skärmdumpar med Python (färdigt)

Har även gjort en modul för att kunna använda ett sådant PhantomJS-skript, i Driver/Screenshot.py.

### screenshot.py (färdigt)

Samt ett exempel på att använda denna mobul i tools/screenshot.py. 

# Vägkarta

  * Asynkron jobbhantering med celery, redis som kö och report-backend
  * WSGI API med bottle.py för att skicka in nya jobb till celery, samt hantera andra saker med de lagrade bilderna och jobben
  * Cronjobb som skickar in alla de lagrade jobben från databas och skickar dem till celery regelbundet
  * Angular.js gränssnitt

# PhantomJS Installation

Kräver node och npm, går att installera från källkod hämtad på deras [github](https://github.com/joyent/node), npm inkluderas i senaste versionen av node. 

Installera PhantomJS globalt så här. 

  sudo npm install -g phantomjs

På Debian blir det rättighetsfel, så det får man fixa i `/usr/local/lib/node_modules´. 


