import tensorflow as tf

def lr_model(feature_num=5):
    inputs = tf.keras.Input((feature_num,))
    pred = tf.keras.layers.Dense(units=1, 
                                 bias_regularizer=tf.keras.regularizers.l2(0.01),
                                 kernel_regularizer=tf.keras.regularizers.l1(0.02),
                                 activation=tf.nn.sigmoid)(inputs)
    lr = tf.keras.Model(inputs, pred)
    lr.compile(loss='binary_crossentropy',
               optimizer=tf.train.AdamOptimizer(0.001),
               metrics=['accuracy'])
    return lr


# lr = lr_model()
# lr.fit(X_train, y_train, epochs=10, batch_size=100, validation_data=(X_test, y_test))
