import React from "react"

import Checkbox from "./Checkbox.coffee"
import HiddenField from "./HiddenField.coffee"
import MultiSelect from "./MultiSelect.coffee"
import NumericField from "./NumericField.coffee"
import ReadonlyField from "./ReadonlyField.coffee"
import Select from "./Select.coffee"
import StringField from "./StringField.coffee"
import TableCell from "./TableCell.coffee"


class TableTransposedCell extends TableCell

  constructor: (props) ->
    super(props)

  get_item: ->
    # The transposed item is the original folder item,
    # stored below the key of the current column (column_key)
    return @props.item[@props.column_key]

  get_column_key: ->
    # The transposed key points to a key inside the transposed item
    return @props.item.item_key or @props.item.column_key

  get_type: (column_key, item) ->
    # true if the field is editable
    editable = @is_edit_allowed column_key, item
    resultfield = @is_result_field column_key, item

    # readonly field
    if not editable
      return "readonly"

    # check if the field is a boolean
    value = @get_value column_key, item
    if typeof(value) == "boolean"
      return "boolean"

    # check if the field is listed in choices
    choices = item.choices or {}
    if column_key of choices
      return "select"

    # check if the field is an interim
    interims = item.interimfields or []
    if interims.length > 0
      interim_keys = item.interimfields.map (interim) ->
        return interim.keyword
      if column_key in interim_keys
        return "interim"

    # check if the field is a calculated field
    if resultfield and item.calculation
      return "calculated"

    # the default
    return "numeric"

  render: ->
    <td className={@props.className}
        colSpan={@props.colspan}
        rowSpan={@props.rowspan}>
      <div className="form-group">
        {@render_before_content()}
        {@render_content()}
        {@render_after_content()}
      </div>
    </td>

export default TableTransposedCell
