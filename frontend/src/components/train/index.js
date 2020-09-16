import React, { Component, Fragment } from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { setClusteredIris } from "../../actions/iris";
import axios from 'axios'

import { ProgressBar } from 'react-bootstrap';
import TrainingBoard from "./TrainingBoard";
import TrainedBoard from "./TrainedBoard";


export class IrisExplore extends Component {
  static propTypes = {
    iris: PropTypes.array.isRequired,
    getIris: PropTypes.func.isRequired,
  };

  constructor(props) {
    super(props);

    this.state = {
      cluster_number: 3,
      percentile: 0,
      status: "idle",
      stop_feeding: false
    };

    this.updateStatus = this.updateStatus.bind(this);
  };

  updateStatus(status){
    console.log("change status to ", status)

    this.setState({status: status})
  };

  componentDidMount() {
  };

  getAllPredictedData() {
    axios.get("/api/predict").then((respData) => {
      let irisData = respData['result'];
      this.props.setClusteredIris(irisData);
    })
  }

  updateProgressStatus(){
     console.log("query train model...")

      let percentile = this.state.percentile;
      if( percentile <= 80 )
      {
        percentile += 10;
        this.setState({percentile: percentile});
      }

      let status = this.state.status
      console.log("now get status is =", status);
      if ("done" === status) {
          this.setState({percentile: 100});
          this.getAllPredictedData();
      } else {
          setTimeout(() => {
              this.updateProgressStatus()
          }, 5000)
      }
  }

  startTrain(){
    console.log("======start train =======")
    this.setState({percentile: 0, stop_feeding: false, status: 'doing'});

    this.props.setClusteredIris([]);

    let cluster_number = this.state.cluster_number;

    axios.post("/api/train/start", {cluster_number: cluster_number}).then((resp)=>{
      console.log("data=", resp.data);

      let percentile = this.state.percentile;
      percentile += 10;
      this.setState({percentile: percentile})

      this.updateProgressStatus()

      setTimeout(()=>{
        this.triggerOnlineTrain()
      }, 10000)  
    })
  }

  stopTrain() {
    axios.post("/api/train/stop").then((resp)=>{
      console.log("stop train process")
      console.log("data=", resp.data);
      this.setState({stop_feeding: true})
    })
  }

  handleChange(e) {
    this.setState({cluster_number: e.target.value});
  }

  onSubmit = e => {
    e.preventDefault();
  }

  render() {
    let cluster_number = this.state.cluster_number;
    let percentile = this.state.percentile

    return (
      <Fragment>
        <form onSubmit={this.onSubmit.bind(this)}>
          <div className="form-group">
            <label>cluster number</label>
            <input
              className="form-control"
              type="text"
              name="cluster_number"
              onChange={this.handleChange.bind(this)}
              value={cluster_number}
            />
          </div>
          <ProgressBar animated now={percentile} label={`${percentile}%`}/>
          <br/>
          <div className="form-group">
            <button type="submit" className="btn btn-primary" onClick={this.startTrain.bind(this)}>start train</button>
            &nbsp;&nbsp;
            <button type="button" className="btn btn-primary" onClick={this.stopTrain.bind(this)}>stop train</button>
          </div>
        </form>

        {
          this.state.percentile === 100 ? 
          <TrainedBoard clusterNumber={cluster_number}></TrainedBoard>
          : 
          <TrainingBoard 
            setHook={hook => this.triggerOnlineTrain = hook} 
            updateStatus={this.updateStatus}
            stop_feeding={this.state.stop_feeding}></TrainingBoard>
        }
      </Fragment>
    );
  }
}

const mapStateToProps = state => ({
});

export default connect(
  mapStateToProps,
  { setClusteredIris }
)(IrisExplore);
