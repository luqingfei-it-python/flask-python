// pages/user_history/user_history.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
      user_list:null,
      dynamic_id:''
  },

// 点击进入详情页
  getdetail(e){
      this.setData({
        dynamic_id: e.currentTarget.dataset.id
      })
    wx.request({
       url: 'http://192.168.43.110:5000/api/detail',
      method: 'GET',
      data: {
        dynamic_id: this.data.dynamic_id
      },
      success: function (res) {
        console.log(res)
        wx.navigateTo({
          url: '../detail/detail?data=' + JSON.stringify(res.data)
        })
      }
    })
  },
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
      this.setData({
        user_list: JSON.parse(options.data).data
      })
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  }
})