(function( $ ) {
$(document).ready(function(){

    window.jarn.i18n.loadCatalog("bika");
    _ = jarn.i18n.MessageFactory('bika');
    window.jarn.i18n.loadCatalog("plone");
    PMF = jarn.i18n.MessageFactory('plone');


    $(".field.ArchetypesReferenceWidget input[name=Contact],.field.ArchetypesReferenceWidget input[name*='\\.Contact']")
       .live('selected', function(){
            // debugger;
        }
   )

});
}(jQuery));
