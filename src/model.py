import tensorflow as tf
from tensorflow.keras.layers import Input, Embedding, Flatten, Concatenate, Dense, Dropout, Multiply
from tensorflow.keras.models import Model

def create_ncf_model(num_users, num_items, embedding_dim=16, layers=[64, 32, 16, 8]):
    # Input layers
    user_input = Input(shape=(1,), name='user_input')
    item_input = Input(shape=(1,), name='item_input')

    # GMF part
    user_embedding_gmf = Embedding(num_users, embedding_dim, name='user_embedding_gmf')(user_input)
    item_embedding_gmf = Embedding(num_items, embedding_dim, name='item_embedding_gmf')(item_input)
    gmf_user_flat = Flatten()(user_embedding_gmf)
    gmf_item_flat = Flatten()(item_embedding_gmf)
    gmf_output = Multiply()([gmf_user_flat, gmf_item_flat])

    # MLP part
    user_embedding_mlp = Embedding(num_users, embedding_dim, name='user_embedding_mlp')(user_input)
    item_embedding_mlp = Embedding(num_items, embedding_dim, name='item_embedding_mlp')(item_input)
    mlp_user_flat = Flatten()(user_embedding_mlp)
    mlp_item_flat = Flatten()(item_embedding_mlp)
    mlp_output = Concatenate()([mlp_user_flat, mlp_item_flat])
    
    for i, nodes in enumerate(layers):
        mlp_output = Dense(nodes, activation='relu', name=f'mlp_layer_{i}')(mlp_output)
        mlp_output = Dropout(0.2)(mlp_output)

    # Combine GMF and MLP
    combined = Concatenate()([gmf_output, mlp_output])
    
    # Final prediction layer
    output = Dense(1, activation='linear', name='prediction')(combined) # Predicting rating

    model = Model(inputs=[user_input, item_input], outputs=output)
    return model

if __name__ == "__main__":
    # Test model creation
    model = create_ncf_model(1000, 2000)
    model.summary()
