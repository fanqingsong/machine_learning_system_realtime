import React, { Component, Fragment } from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { getIris } from "../../actions/iris";
import axios from 'axios'

var async = require("async");


export class Iris extends Component {
  static propTypes = {
    irisDataFromDB: PropTypes.array.isRequired,
    getIris: PropTypes.func.isRequired,
    updateStatus: PropTypes.func.isRequired,
    stop_feeding: PropTypes.bool.isRequired
  };

  constructor(props) {
    super(props);

    this.triggerOnlineTrain = this.triggerOnlineTrain.bind(this);

    this.state = {
      allIrisData: [],
      oneTrainingIris: undefined,
      trainedIrisData: []
    }
  };

  componentWillReceiveProps(newProps) {
    console.log('Component WILL RECEIVE PROPS!')
    console.log(newProps)

    console.log(this.state)
    console.log(this.props)
    let irisDataFromDB = newProps.irisDataFromDB;
    console.log(irisDataFromDB)

    this.setState({allIrisData: irisDataFromDB})  

    console.log(this.state)
  }

  componentWillUpdate(nextProps, nextState) {
    console.log('Component WILL UPDATE!');
    console.log(nextProps)
    console.log(nextState)

    console.log(this.props)
    // old props
    let irisDataFromDB = this.props.irisDataFromDB;
    console.log(irisDataFromDB)
  }

  componentDidMount() {
      this.props.setHook(this.triggerOnlineTrain)

      this.props.getIris()
  };

  triggerOnlineTrain() {
    let allIrisData = this.state.allIrisData;
    console.log("all", allIrisData)

    this.props.updateStatus("doing")

    async.mapSeries(allIrisData, function(oneIris, callback){
      if (this.props.stop_feeding){
        callback(null, null)
        return
      }

      let oneTrainingIris = oneIris;
      console.log("current training iris =", oneTrainingIris)

      this.setState({oneTrainingIris: oneTrainingIris});

      let {sepal_len, sepal_width, petal_len, petal_width} = oneTrainingIris;
      let postData = {
        sepal_len,
        sepal_width,
        petal_len,
        petal_width
      }
  
      axios.post("/api/feed", postData).then((resp)=>{
        console.log("data=", resp.data);
          setTimeout(() => {
            oneTrainingIris.trained = true;

            // update view because of changed trained attr
            this.setState({allIrisData: allIrisData});

            callback(null, null)
          }, 4000);
      })
    }.bind(this), function(err, results) {
      // results is now an array of stats for each file
      console.log("feeding data over!")
      this.props.updateStatus("done")
    }.bind(this));
  };

  render() {
    let oneTrainingIris = this.state.oneTrainingIris;
    let allTrainingIrisData = [];
    if( oneTrainingIris ) {
      allTrainingIrisData.push(oneTrainingIris);
    }
    
    return (
      <Fragment>
        <h2>Iris Data being learned</h2>
        <table className="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>sepal_len</th>
              <th>sepal_width</th>
              <th>petal_len</th>
              <th>petal_width</th>
              <th>category</th>
            </tr>
          </thead>
          <tbody>
            {allTrainingIrisData.map(oneIris => (
              <tr key={oneIris.id}>
                <td>{oneIris.id}</td>
                <td>{oneIris.sepal_len}</td>
                <td>{oneIris.sepal_width}</td>
                <td>{oneIris.petal_len}</td>
                <td>{oneIris.petal_width}</td>
                <td>{oneIris.category}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <hr></hr>
        <h2>Iris Data to be learned one by one</h2>
        <table className="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>sepal_len</th>
              <th>sepal_width</th>
              <th>petal_len</th>
              <th>petal_width</th>
              <th>category</th>
            </tr>
          </thead>
          <tbody>
            {this.state.allIrisData.filter(oneIris=>oneIris.trained!=true).map(oneIris => (
              <tr key={oneIris.id}>
                <td>{oneIris.id}</td>
                <td>{oneIris.sepal_len}</td>
                <td>{oneIris.sepal_width}</td>
                <td>{oneIris.petal_len}</td>
                <td>{oneIris.petal_width}</td>
                <td>{oneIris.category}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Fragment>
    );
  }
}

const mapStateToProps = state => ({
  irisDataFromDB: state.iris.iris
});

export default connect(
  mapStateToProps,
  { getIris }
)(Iris);
