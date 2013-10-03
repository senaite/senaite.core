(function( $ ) {
$(document).ready(function(){

    _ = jarn.i18n.MessageFactory('bika');
    PMF = jarn.i18n.MessageFactory('plone');


    $(".field.ArchetypesReferenceWidget input[name=Contact],.field.ArchetypesReferenceWidget input[name*='\\.Contact']")
       .live('selected', function(){
            // debugger;
        }
   )

});
}(jQuery));
