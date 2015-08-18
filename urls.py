import handlers.auth
import handlers.reps
import handlers.quotes
#import handlers.features
import handlers.options
import handlers.items
import handlers.sara

handler_urls = [
    (r'/login', handlers.auth.Login),
    (r'/logout', handlers.auth.Logout),

    (r'/sara', handlers.sara.SaraMode),

    (r'/build', handlers.quotes.Build),

    (r'/', handlers.quotes.Search),

    (r'/quote/new', handlers.quotes.New),
    (r'/quote/([\w]+)', handlers.quotes.Edit),
    (r'/quote/([\w]+)/new_item', handlers.quotes.NewItem),
    


    (r'/items', handlers.items.List),
    (r'/item/([\w]+)', handlers.items.Edit),
    (r'/item/([\w]+)/delete', handlers.items.Delete),
    (r'/item/([\w]+)/sort', handlers.items.Sort),

    
    (r'/options', handlers.options.List),
    (r'/option/new', handlers.options.New),
    (r'/option/([\w]+)', handlers.options.List),
    (r'/option/([\w]+)/delete', handlers.options.Delete),

#    (r'/feature/([\w]+)/options', handlers.options.List),
#    (r'/feature/([\w]+)/option/new', handlers.options.New),
#    (r'/feature/([\w]+)/option/([\w]+)', handlers.options.Edit),
#    (r'/feature/([\w]+)/option/([\w]+)/delete', handlers.options.Delete),

    (r'/reps', handlers.reps.List),
    (r'/reps/search', handlers.reps.Autocomplete),
    (r'/rep/new', handlers.reps.New),
    (r'/rep/([\w]+)', handlers.reps.Edit),
    (r'/rep/([\w]+)/delete', handlers.reps.Delete),
    (r'/reps/zip/([\w]+)', handlers.reps.Zip),
    
]
