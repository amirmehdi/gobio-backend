'use strict';

module.exports.config = async (event) => {
  return {
    statusCode: 200,
    body: JSON.stringify(
      {
        siteBucket: `https://${process.env.SITES_BUCKET}.s3.amazonaws.com/`,
        userPoolId: process.env.USER_POOL_ID,
        clientId: process.env.CLIENT_ID,
        version: '1.0',
      },
      null,
      2
    ),
  };

};
