import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="vanshsingh@2005", database="car_rental_db"
    )

# Function to execute queries
def execute_query(query, params=None, fetch=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    if fetch:
        result = cursor.fetchall()
        conn.close()
        return result
    conn.commit()
    conn.close()

# Streamlit UI
st.title(" Car Rental Management System")
st.write("At EasyCarRentals, we make your travel experience seamless and enjoyable. Whether you're planning a weekend getaway, a business trip, or need a car for daily commuting, we've got you covered with a wide range of vehicles to suit your needs")
menu = ["Home", "Manage Cars", "Manage Rentals", "View Insights"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Manage Cars":
    st.subheader("Manage Cars")
    option = st.selectbox("Choose an action", ["Add Car", "View Cars", "Update Car", "Delete Car"])

    if option == "Add Car":
        brand = st.text_input("Brand")
        model = st.text_input("Model")
        year = st.number_input("Year", min_value=1990, max_value=2030, step=1)
        status = st.selectbox("Availability", ["Available", "Rented"])
        if st.button("Add Car"):
            execute_query("INSERT INTO Cars (brand, model, year, status) VALUES (%s, %s, %s, %s)",
                          (brand, model, year, status))
            st.success("Car added successfully!")
    
    elif option == "View Cars":
        cars = execute_query("SELECT * FROM Cars", fetch=True)
        df = pd.DataFrame(cars, columns=["ID", "Brand", "Model", "Year", "Status"])
        st.dataframe(df)
    
    elif option == "Update Car":
        car_id = st.number_input("Car ID", min_value=1, step=1)
        
        new_status = st.selectbox("New Status", [True,False])
        
        if st.button("Update Car"):
            execute_query("UPDATE Cars SET availability=%s WHERE id=%s", (new_status, car_id))
            st.success("Car status updated!")

    elif option == "Delete Car":
        car_id = st.number_input("Car ID", min_value=1, step=1)
        if st.button("Delete Car"):
            execute_query("DELETE FROM Cars WHERE id=%s", (car_id,))
            st.success("Car deleted successfully!")

elif choice == "Manage Rentals":
    st.subheader("Manage Rentals")
    action = st.selectbox("Choose an action", ["Rent Car", "Return Car", "View Available Cars"])
    
    if action == "Rent Car":
        car_id = st.number_input("Car ID", min_value=1, step=1)
        rental_date = st.date_input("Rent Date")
        if st.button("Rent Car"):
            execute_query("INSERT INTO Rentals (car_id, rental_date) VALUES ( %s, %s)",
                          (car_id, rental_date))
            execute_query("UPDATE Cars SET availability=False WHERE id=%s", (car_id,))
            st.success("Car rented successfully!")
    
    elif action == "Return Car":
        rental_id = st.number_input("Rental ID", min_value=1, step=1)
        if st.button("Return Car"):
            execute_query("DELETE FROM Rentals WHERE id=%s", (rental_id,))
            execute_query("UPDATE Cars SET status='Available' WHERE id=(SELECT car_id FROM Rentals WHERE id=%s)", (rental_id,))
            st.success("Car returned successfully!")
    
    elif action == "View Available Cars":
        available_cars = execute_query("SELECT * FROM Cars WHERE status='Available'", fetch=True)
        df = pd.DataFrame(available_cars, columns=["ID", "Brand", "Model", "Year", "Status"])
        st.dataframe(df)

elif choice == "View Insights":
    st.subheader("Rental Insights")
    rentals = execute_query("SELECT brand, COUNT(*) FROM Rentals JOIN Cars ON Rentals.car_id = Cars.id GROUP BY brand", fetch=True)
    df = pd.DataFrame(rentals, columns=["Brand", "Total Rentals"])
    
    fig, ax = plt.subplots()
    ax.bar(df["Brand"], df["Total Rentals"])
    plt.xlabel("Car Brand")
    plt.ylabel("Total Rentals")
    plt.title("Most Rented Cars")
    st.pyplot(fig)
    
    st.subheader("Monthly Rentals")
    monthly_rentals = execute_query("SELECT MONTH(rental_date), COUNT(*) FROM Rentals GROUP BY MONTH(rental_date)", fetch=True)
    df_months = pd.DataFrame(monthly_rentals, columns=["Month", "Total Rentals"])
    
    fig2, ax2 = plt.subplots()
    ax2.bar(df_months["Month"], df_months["Total Rentals"])
    plt.xlabel("Month")
    plt.ylabel("Total Rentals")
    plt.title("Monthly Rental Trends")
    plt.xticks(range(1, 13), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    st.pyplot(fig2)


