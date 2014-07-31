(function($) {

    // Define querywidget namespace if it doesn't exist
    if (typeof($.querywidget) == "undefined") {
        $.querywidget = {
            config: {},
            initialized: false
        };
    }

    // Create a select menu
    $.querywidget.createSelect = function (values, selectedvalue, className, name) {

        // Create select
        var select = $(document.createElement('select'))
                            .addClass(className)
                            .attr('name', name);
        $.each(values, function (i, val) {
            if ((typeof(val.enabled) == "undefined") || (val.enabled)) {
                var option = $(document.createElement('option'))
                                .attr('value', i)
                                .html(val.title);
                if (i == selectedvalue) {
                    option.attr('selected', 'selected');
                }
                if (typeof(val.group) != "undefined") {
                    var optgroup = select.find("optgroup[label=" + val.group + "]");
                    if (optgroup.length == 0) {
                        optgroup = $(document.createElement('optgroup'))
                                    .attr('label', val.group);
                        optgroup.append(option);
                        select.append(optgroup);
                    } else {
                        optgroup.append(option);
                    }
                } else {
                    select.append(option);
                }
            }
        });
        return select;
    };

    // Create a queryindex select menu
    $.querywidget.createQueryIndex = function (value) {
        return $.querywidget.createSelect($.querywidget.config.indexes,
                            value,
                            'queryindex',
                            'query.i:records');
    };

    // Create a queryoperator select menu
    $.querywidget.createQueryOperator = function (index, value) {
        return $.querywidget.createSelect($.querywidget.config.indexes[index].operators,
                            value,
                            'queryoperator',
                            'query.o:records');
    };

    $.querywidget.createWidget = function (type, index) {
        wrapper = $(document.createElement('div'));
        switch (type) {
            case 'StringWidget':
                wrapper.load($("base").attr('href') + '/@@archetypes-querywidget-stringwidget');
                break;
            case 'RelativeDateWidget':
                wrapper.load($("base").attr('href') + '/@@archetypes-querywidget-relativedatewidget');
                break;
            case 'DateWidget':
                wrapper.load($("base").attr('href') + '/@@archetypes-querywidget-datewidget',
                    function(){
                        $(this).find('input')
                            .dateinput().removeClass('date')
                            .change(function(e){
                                $.querywidget.updateSearch();
                            });
                    });
                break;
            case 'DateRangeWidget':
                wrapper.load($("base").attr('href') + '/@@archetypes-querywidget-daterangewidget',
                    function(){
                        $(this).find('input')
                            .dateinput().removeClass('date')
                            .change(function(e){
                                $.querywidget.updateSearch();
                            });
                    });
                break;
            case 'ReferenceWidget':
                wrapper.load($("base").attr('href') + '/@@archetypes-querywidget-referencewidget');
                break;
            case 'RelativePathWidget':
                wrapper.load($("base").attr('href') + '/@@archetypes-querywidget-relativepathwidget');
                break;
            case 'MultipleSelectionWidget':
                wrapper.load($("base").attr('href') + '/@@archetypes-querywidget-multipleselectionwidget',
                            {'index': index});
                break;
            default:
                wrapper.load($("base").attr('href') + '/@@archetypes-querywidget-emptywidget');
                break;
        }
        return wrapper;
    };

    $.querywidget.getCurrentWidget  = function (node) {
        if (!node.length) {
            return;
        }
        var classes = node.attr('class').split(' ');
        for (var i in classes) {
            if (classes[i].indexOf('Widget') != -1) {
                var classname = classes[i];
                return classname.slice(0,1).toUpperCase() + classname.slice(1);
            }
        }
    };

    /* Should livesearch update, looking at the last changed element? */
    $.querywidget.shouldUpdate = function(node, e) {
        var criteria = $(node).parents('.criteria');
        var operator = criteria.children('.queryoperator').val();
        var values = criteria.children('.queryvalue');
        var index = criteria.children('.queryindex').val();
        var querywidget = criteria.children('.querywidget');
        var widgetname = $.querywidget.config.indexes[index].operators[operator].widget;
        switch (widgetname) {
            case 'MultipleSelectionWidget':
                return true;
            case 'DateRangeWidget':
                /* fall through */
            case 'DateWidget':
                /* We use a datepicker which has it's own change handler. That
                   one does the refresh. */
                return false;
            case 'RelativeDateWidget':
                return true;
            default:
                /* Backspace and delete should force update */
                if (e.keyCode == 8 || e.keyCode == 46) {
                    return true;
                }

                if ($(node).val().length >= 3) {
                    return true;
                }
                break;
        }
        return false;
    };

    $.querywidget.updateSearch = function () {
        var base_url = $("base").attr("href");
        // if(base_url.indexOf("portal_factory") != -1) {
        //     base_url = base_url.split("/").slice(0, -2).join("/");
        // }
        var query = base_url + "/@@querybuilder_html_results?";
        catalog_name = $("#querywidget_catalog_name").val();
        var querylist  = ['catalog_name='+catalog_name];
        var items = $('.ArchetypesQueryWidget .queryindex');
        if (!items.length) {
            return;
        }
        items.each(function () {
            var results = $(this).parents('.criteria').children('.queryresults');
            var index = $(this).val();
            var operator = $(this).parents('.criteria').children('.queryoperator').val();
            var widget = $.querywidget.config.indexes[index].operators[operator].widget;
            var querywidget = $(this).parents('.criteria').find('.querywidget');
            querylist.push('query.i:records=' + index);
            querylist.push('query.o:records=' + operator);

            function getDateWidgetValue(obj) {
                // Get values from the date widget instead of the field itself, as the value
                // of the field isn't yet updated at this point in the "change" event.
                value = (obj.data('dateinput') && obj.data('dateinput').getValue('mm/dd/yyyy')) || '';
                return value;
            }

            switch (widget) {
                case 'DateWidget':
                    value = getDateWidgetValue($(this).parents('.criteria').find('.queryvalue'));
                    if (value) {
                        querylist.push('query.v:records=' + value);
                    }
                    break;
                case 'DateRangeWidget':
                    start_date = getDateWidgetValue($(querywidget.children('input')[0]));
                    end_date = getDateWidgetValue($(querywidget.children('input')[1]));

                    querylist.push('query.v:records:list=' + start_date);
                    querylist.push('query.v:records:list=' + end_date);
                    break;
                case 'MultipleSelectionWidget':
                    querywidget.find('input:checked').each(function () {
                        querylist.push('query.v:records:list=' + $(this).val());
                    });
                    break;
                default:
                    value = $(this).parents('.criteria').find('.queryvalue').val();
                    push_string = 'query.v:records=';
                    if (value) {
                        push_string = push_string + value;
                    }
                    querylist.push(push_string);
                    break;
            }
            if (querylist.length){
                $.get($("base").attr('href') + '/@@querybuildernumberofresults?' + querylist.join('&'),
                      {},
                      function (data) { results.html(data); });
            }
        });
        query += querylist.join('&');
        query += '&sort_on=' + $('#sort_on').val();
        if ($('#sort_order:checked').length > 0) {
            query += '&sort_order=reverse';
        }
        $.get(query, {}, function (data) { $('.ArchetypesQueryWidget .previewresults').html(data); });
    };

    // Enhance for javascript browsers
    $(document).ready(function () {

        // Init
        $.querywidget.init();


    });

    // Init widget
    $.querywidget.init = function () {

        // Check if already initialized
        if ($.querywidget.initialized == true) {

            // Return nothing done
            return false;
        }

        // Set initialized
        $.querywidget.initialized = true;

        // Get configuration
        catalog_name = $("#querywidget_catalog_name").val();
        var querylist  = [];
        $.getJSON($("base").attr("href") + '/@@querybuilderjsonconfig?catalog_name='+catalog_name, function (data) {
            $.querywidget.config = data;

            // Find querywidgets
            $(".ArchetypesQueryWidget").each(function () {

                // Get object
                var obj = $(this);

                // Hide controls used for non-javascript only
                obj.find(".addIndexButton").hide();
                obj.find(".multipleSelectionWidget dt").show();
                obj.find(".multipleSelectionWidget dd").addClass('widgetPulldownMenu').hide();

                $('div.queryindex').each(function () {
                    $(this).before(
                        $(document.createElement('div'))
                            .addClass('queryresults discreet')
                            .html('')
                    );
                    $(this).replaceWith($.querywidget.createQueryIndex($(this).children('input').val()));
                });
                $('div.queryoperator').each(function () {
                    $(this).replaceWith($.querywidget.createQueryOperator($(this).parents('.criteria').children('.queryindex').val(),
                                                            $(this).children('input').val()));
                });
                $.querywidget.updateSearch();
            });
        });

        $('.multipleSelectionWidget dt').live('click', function () {
            $(this).parent().children('dd').toggle();
        });

        /* Clicking outside a multipleSelectionWidget will close all open
           multipleSelectionWidgets */
        $(window).click(function(event){
            if ($(event.target).parents('.multipleSelectionWidget').length) {
                return;
            }

            $('.multipleSelectionWidget dd').hide();
        });

        $('.queryindex').live('change', function () {
            var index = $(this).find(':selected')[0].value;
            $(this).parents(".criteria").children('.queryoperator')
                .replaceWith($.querywidget.createQueryOperator(index, ''));
            var operatorvalue = $(this).parents('.criteria').children('.queryoperator').val();
            var widget = $.querywidget.config.indexes[index].operators[operatorvalue].widget;
            var querywidget = $(this).parent(".criteria").find('.querywidget');
            if ((widget != $.querywidget.getCurrentWidget(querywidget)) || (widget == 'MultipleSelectionWidget')) {
                querywidget.replaceWith($.querywidget.createWidget(widget, index));
            }
            $.querywidget.updateSearch();

        });

        $('.queryoperator').live('change', function () {
            var index = $(this).parents('.criteria').children('.queryindex').val();
            var operatorvalue = $(this).children(':selected')[0].value;
            var widget = $.querywidget.config.indexes[index].operators[operatorvalue].widget;
            var querywidget = $(this).parent().find('.querywidget');
            if (widget != $.querywidget.getCurrentWidget(querywidget)) {
                querywidget.replaceWith($.querywidget.createWidget(widget, index));
            }
            $.querywidget.updateSearch();
        });

        $('#sort_on,#sort_order').live('change', function () {
            $.querywidget.updateSearch();
        });

        $('.multipleSelectionWidget input').live('change', function () {
            var widget = $(this).parents('.multipleSelectionWidget');
            var selected_values = [];
            widget.find('input:checked').each(function () {
                selected_values.push($(this).parent().children('span').html());
            });
            widget.find('.multipleSelectionWidgetTitle')
                .attr('title', selected_values.join(', '))
                .html(selected_values.join(', '));
            $.querywidget.updateSearch();
        });

        $('.queryvalue').live('keyup', function (e) {
            if ($.querywidget.shouldUpdate(this, e)) {
                $.querywidget.updateSearch();
            }
        });

        $('.queryvalue').live('keydown', function (e) {
            if (e.keyCode == 13) {
                return false;
            }
        });

        $('.addIndex').live('change', function () {
            var index = $(this).find(':selected')[0].value;
            var criteria = $(this).parents('.criteria');
            var newcriteria = $(document.createElement('div'))
                                .addClass('criteria');

            newcriteria.append(
                    $(document.createElement('div'))
                        .addClass('queryresults discreet')
                        .html('')
                );
            newcriteria.append($.querywidget.createQueryIndex(index));
            var operator = $.querywidget.createQueryOperator(index,'');
            newcriteria.append(operator);
            var operatorvalue = $(operator.children()[0]).attr('value');
            newcriteria.append($.querywidget.createWidget($.querywidget.config.indexes[index].operators[operatorvalue].widget, index));

            $.get($("base").attr('href') + '/@@archetypes-querywidget-removecriterialink',
              {}, function (data) { newcriteria.append(data);});

            criteria.before(newcriteria);
            $(this).val('');
            $.querywidget.updateSearch();
        });

        $('.removecriteria').live('click', function () {
            $(this).parents('.criteria').remove();
            $.querywidget.updateSearch();
            return false;
        });
    };
})(jQuery);
