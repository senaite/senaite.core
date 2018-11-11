import React from "react"

import "./Loader.css"


class Loader extends React.Component

  render: ->
    if not @props.loading
      # render a placeholder to avoid vertical jumps
      return <div className="loader"></div>

    <div className="loader">
      <span className="dot dot_1"></span>
      <span className="dot dot_2"></span>
      <span className="dot dot_3"></span>
      <span className="dot dot_4"></span>
    </div>


export default Loader
