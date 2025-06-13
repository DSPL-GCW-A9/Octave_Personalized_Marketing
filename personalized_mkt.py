import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import requests
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .strategy-box {
        background-color: #e8f4fd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #1f77b4;
        margin: 1rem 0;
    }
    .cluster-description {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Data loading function with caching
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load data from Google Sheets CSV"""
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRZgNxyt--8_BClE5Aa371WTaNJ38f0lhiGeGAUre2LEhrzeIHQtSYxvBaMnJnAbodWhgitFfqPmUj2/pub?output=csv"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Ensure numeric columns are properly formatted
        numeric_cols = ['luxury_sales', 'fresh_sales', 'dry_sales', 'total_sales', 'predicted_customer_segmentation']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Cluster mapping
CLUSTER_MAPPING = {
    1: "Bulk Dry Shoppers – Urban",
    2: "Fresh-Focused Families – Suburban", 
    3: "Balanced Shoppers – Urban",
    4: "Bulk Dry Shoppers – Suburban",
    5: "Balanced Shoppers – Suburban",
    6: "Fresh-Focused Families – Urban"
}

# Marketing strategies
MARKETING_STRATEGIES = {
    "Bulk Dry Shoppers – Urban": {
        "primary": "📱 Push bundle discounts via mobile app",
        "secondary": "🏪 In-store bulk purchase promotions",
        "channels": ["Mobile App", "Email", "In-store displays"],
        "offers": ["Buy 3 Get 1 Free on dry goods", "20% off bulk purchases over Rs.100", "Monthly dry goods subscription box"],
        "timing": "Weekend promotions, month-end bulk deals"
    },
    "Bulk Dry Shoppers – Suburban": {
        "primary": "🚚 Home delivery discounts for bulk orders",
        "secondary": "📧 Email campaigns with bulk savings",
        "channels": ["Email", "Direct Mail", "Local newspaper ads"],
        "offers": ["Free delivery on orders over Rs.75", "25% off quarterly bulk orders", "Family pack discounts"],
        "timing": "Monthly family budget cycles, seasonal stocking"
    },
    "Fresh-Focused Families – Urban": {
        "primary": "🥬 Weekly fresh produce delivery deals",
        "secondary": "⏰ Same-day fresh delivery promotions",
        "channels": ["Mobile App", "Social Media", "Local food blogs"],
        "offers": ["Daily fresh deals", "Organic produce premium membership", "Recipe-based fresh bundles"],
        "timing": "Daily fresh arrivals, weekend meal prep"
    },
    "Fresh-Focused Families – Suburban": {
        "primary": "🚗 Drive-through fresh pickup services",
        "secondary": "👨‍👩‍👧‍👦 Family-oriented fresh meal kits",
        "channels": ["Local community groups", "School partnerships", "Social Media"],
        "offers": ["Fresh family meal plans", "Kids' lunch prep kits", "Weekend BBQ fresh bundles"],
        "timing": "School calendar aligned, weekend family time"
    },
    "Balanced Shoppers – Urban": {
        "primary": "🎯 Cross-category coupons via app notifications",
        "secondary": "🛒 Smart shopping list recommendations",
        "channels": ["Mobile App", "Email", "Targeted online ads"],
        "offers": ["Mix & match discounts", "Smart basket rewards", "Loyalty points multiplier"],
        "timing": "Weekly shopping patterns, payday cycles"
    },
    "Balanced Shoppers – Suburban": {
        "primary": "📱 SMS cross-category promotions",
        "secondary": "🏪 In-store balanced shopping rewards",
        "channels": ["SMS", "Local radio", "Community bulletin boards"],
        "offers": ["Balanced basket bonuses", "Weekly shopping rewards", "Seasonal variety packs"],
        "timing": "Weekly family shopping trips, seasonal transitions"
    }
}

def main():
    # Header
    st.markdown('<h1 class="main-header">🛒 Customer Segmentation Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading real-time data from Google Sheets..."):
        df = load_data()
    
    if df is None:
        st.error("Failed to load data. Please check the connection.")
        return
    
    # Add cluster names to dataframe
    df['cluster_name'] = df['predicted_customer_segmentation'].map(CLUSTER_MAPPING)
    
    # Sidebar filters
    st.sidebar.header("🎛️ Filters")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Filter by cluster
    clusters = sorted(df['predicted_customer_segmentation'].unique())
    cluster_names = [CLUSTER_MAPPING[c] for c in clusters]
    selected_clusters = st.sidebar.multiselect(
        "Select Customer Segments:",
        options=cluster_names,
        default=cluster_names
    )
    
    # Filter by city
    cities = sorted(df['outlet_city'].unique())
    selected_cities = st.sidebar.multiselect(
        "Select Cities:",
        options=cities,
        default=cities
    )
    
    # Filter by area
    areas = sorted(df['Area'].unique())
    selected_areas = st.sidebar.multiselect(
        "Select Areas:",
        options=areas,
        default=areas
    )
    
    # Apply filters
    filtered_df = df[
        (df['cluster_name'].isin(selected_clusters)) &
        (df['outlet_city'].isin(selected_cities)) &
        (df['Area'].isin(selected_areas))
    ]
    
    # Show filter summary
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**📊 Filtered Data Summary:**")
    st.sidebar.markdown(f"- Total Customers: {len(filtered_df):,}")
    st.sidebar.markdown(f"- Cities: {len(selected_cities)}")
    st.sidebar.markdown(f"- Segments: {len(selected_clusters)}")
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Cluster Summary", "💰 Sales Trends", "🏙️ City-Wise View", "🎯 Marketing Strategy"])
    
    with tab1:
        st.header("Customer Segment Overview")
        
        if len(filtered_df) == 0:
            st.warning("No data available for the selected filters.")
            return
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Customers</h3>
                <h2>{len(filtered_df):,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_total_sales = filtered_df['total_sales'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h3>Avg Total Sales</h3>
                <h2>Rs.{avg_total_sales:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_revenue = filtered_df['total_sales'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Revenue</h3>
                <h2>Rs.{total_revenue:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            unique_cities = filtered_df['outlet_city'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h3>Active Cities</h3>
                <h2>{unique_cities}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Cluster distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Customer Distribution by Segment")
            st.caption("📊 Shows the proportion of customers in each behavioral segment. Use this to identify your largest customer groups and prioritize marketing efforts accordingly.")
            cluster_counts = filtered_df['cluster_name'].value_counts()
            fig_pie = px.pie(
                values=cluster_counts.values,
                names=cluster_counts.index,
                title="Customer Segments Distribution"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("Urban vs Suburban Distribution")
            st.caption("🏙️ Compares urban vs suburban customer distribution. This helps determine whether to focus marketing on city centers or suburban areas.")
            area_counts = filtered_df['Area'].value_counts()
            fig_area = px.bar(
                x=area_counts.index,
                y=area_counts.values,
                title="Customer Distribution by Area",
                color=area_counts.index,
                color_discrete_map={'Urban': '#1f77b4', 'Sub Urban': '#ff7f0e'}
            )
            st.plotly_chart(fig_area, use_container_width=True)
        
        # Cluster descriptions
        st.subheader("Segment Characteristics")
        for cluster_name in selected_clusters:
            cluster_data = filtered_df[filtered_df['cluster_name'] == cluster_name]
            if len(cluster_data) > 0:
                avg_luxury = cluster_data['luxury_sales'].mean()
                avg_fresh = cluster_data['fresh_sales'].mean()
                avg_dry = cluster_data['dry_sales'].mean()
                customer_count = len(cluster_data)
                
                st.markdown(f"""
                <div class="cluster-description">
                    <h4>{cluster_name}</h4>
                    <p><strong>Customers:</strong> {customer_count:,} | 
                    <strong>Avg Luxury:</strong> Rs.{avg_luxury:.2f} | 
                    <strong>Avg Fresh:</strong> Rs.{avg_fresh:.2f} | 
                    <strong>Avg Dry:</strong> Rs.{avg_dry:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.header("Sales Performance Analysis")
        
        if len(filtered_df) == 0:
            st.warning("No data available for the selected filters.")
            return
        
        # Sales by category
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sales by Category")
            st.caption("💰 Total revenue breakdown by product category. Luxury items typically have higher margins, while fresh and dry goods drive volume.")
            category_sales = {
                'Luxury': filtered_df['luxury_sales'].sum(),
                'Fresh': filtered_df['fresh_sales'].sum(),
                'Dry': filtered_df['dry_sales'].sum()
            }
            
            fig_category = px.bar(
                x=list(category_sales.keys()),
                y=list(category_sales.values()),
                title="Total Sales by Product Category",
                color=list(category_sales.keys()),
                color_discrete_map={'Luxury': 'gold', 'Fresh': 'green', 'Dry': 'brown'}
            )
            fig_category.update_layout(yaxis_title="Sales (Rs.)")
            st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            st.subheader("Average Sales by Segment")
            st.caption("📈 Shows spending patterns across customer segments. Identify which segments spend more on which categories to tailor product recommendations.")
            segment_sales = filtered_df.groupby('cluster_name')[['luxury_sales', 'fresh_sales', 'dry_sales']].mean()
            
            fig_segment = px.bar(
                segment_sales,
                title="Average Sales by Customer Segment",
                barmode='group'
            )
            fig_segment.update_layout(xaxis_title="Customer Segment", yaxis_title="Average Sales (Rs.)")
            st.plotly_chart(fig_segment, use_container_width=True)
        
        # Sales distribution
        st.subheader("Sales Distribution Analysis")
        st.caption("📊 Deep dive into customer spending patterns to understand revenue distribution and identify high-value customers.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption("📈 Distribution of total sales per customer. Look for peaks to identify common spending amounts and outliers for VIP customers.")
            fig_hist = px.histogram(
                filtered_df,
                x='total_sales',
                nbins=30,
                title="Total Sales Distribution",
                color_discrete_sequence=['#1f77b4']
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.caption("🎯 Relationship between fresh and dry goods spending by segment. Bubble size = luxury spending. Helps identify cross-selling opportunities.")
            fig_scatter = px.scatter(
                filtered_df,
                x='fresh_sales',
                y='dry_sales',
                color='cluster_name',
                size='luxury_sales',
                title="Fresh vs Dry Sales by Segment",
                hover_data=['outlet_city', 'total_sales']
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab3:
        st.header("City-Wise Performance")
        
        if len(filtered_df) == 0:
            st.warning("No data available for the selected filters.")
            return
        
        # City performance metrics
        city_metrics = filtered_df.groupby('outlet_city').agg({
            'Customer_ID': 'count',
            'total_sales': ['sum', 'mean'],
            'luxury_sales': 'mean',
            'fresh_sales': 'mean',
            'dry_sales': 'mean'
        }).round(2)
        
        city_metrics.columns = ['Customer_Count', 'Total_Revenue', 'Avg_Sales', 'Avg_Luxury', 'Avg_Fresh', 'Avg_Dry']
        city_metrics = city_metrics.sort_values('Total_Revenue', ascending=False)
        
        # Top performing cities
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Cities by Revenue")
            st.caption("🏆 Identifies highest revenue-generating cities. Focus expansion and premium services in these locations.")
            top_cities = city_metrics.head(10)
            fig_top_cities = px.bar(
                x=top_cities.index,
                y=top_cities['Total_Revenue'],
                title="Top 10 Cities by Total Revenue"
            )
            fig_top_cities.update_layout(xaxis_title="City", yaxis_title="Total Revenue (Rs.)")
            fig_top_cities.update_xaxes(tickangle=45)
            st.plotly_chart(fig_top_cities, use_container_width=True)
        
        with col2:
            st.subheader("Average Sales per Customer by City")
            st.caption("💎 Shows customer value by location. High values indicate affluent areas suitable for premium product positioning.")
            fig_avg_sales = px.bar(
                x=city_metrics.index,
                y=city_metrics['Avg_Sales'],
                title="Average Sales per Customer by City"
            )
            fig_avg_sales.update_layout(xaxis_title="City", yaxis_title="Average Sales (Rs.)")
            fig_avg_sales.update_xaxes(tickangle=45)
            st.plotly_chart(fig_avg_sales, use_container_width=True)
        
        # City-wise segment distribution
        st.subheader("Customer Segments by City")
        st.caption("🗺️ Heatmap showing which customer segments dominate in each city. Darker colors = more customers. Use this to localize marketing strategies.")
        city_segments = filtered_df.groupby(['outlet_city', 'cluster_name']).size().unstack(fill_value=0)
        
        fig_heatmap = px.imshow(
            city_segments.T,
            title="Customer Segment Distribution Across Cities",
            color_continuous_scale="Blues",
            aspect="auto"
        )
        fig_heatmap.update_layout(
            xaxis_title="City",
            yaxis_title="Customer Segment"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Detailed city table
        st.subheader("Detailed City Performance")
        st.caption("📋 Complete city metrics table. Sort by any column to find insights. Export for further analysis or reporting.")
        st.dataframe(city_metrics, use_container_width=True)
    
    with tab4:
        st.header("🎯 Dynamic Marketing Strategy")
        
        if len(filtered_df) == 0:
            st.warning("No data available for the selected filters.")
            return
        
        # Strategy overview
        st.subheader("Recommended Marketing Strategies")
        st.markdown("*Strategies update dynamically based on your selected filters*")
        
        # Generate strategies for selected segments
        for cluster_name in selected_clusters:
            cluster_data = filtered_df[filtered_df['cluster_name'] == cluster_name]
            
            if len(cluster_data) == 0:
                continue
            
            strategy = MARKETING_STRATEGIES.get(cluster_name, {})
            customer_count = len(cluster_data)
            avg_sales = cluster_data['total_sales'].mean()
            top_cities = cluster_data['outlet_city'].value_counts().head(3)
            areas = cluster_data['Area'].value_counts()
            
            st.markdown(f"""
            <div class="strategy-box">
                <h3>📊 {cluster_name}</h3>
                <p><strong>Target Audience:</strong> {customer_count:,} customers | <strong>Avg Sales:</strong> Rs.{avg_sales:.2f}</p>
                <p><strong>Top Cities:</strong> {', '.join(top_cities.index.tolist())}</p>
                <p><strong>Area Focus:</strong> {', '.join([f"{area} ({count})" for area, count in areas.items()])}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Use regular markdown for better compatibility
            st.markdown(f"**🎯 Primary Strategy:**")
            st.markdown(f"**{strategy.get('primary', 'Custom strategy needed')}**")
            
            st.markdown(f"**🎯 Secondary Strategy:**")
            st.markdown(f"{strategy.get('secondary', 'Custom strategy needed')}")
            
            st.markdown(f"**📱 Recommended Channels:**")
            st.markdown(f"{', '.join(strategy.get('channels', ['Custom channels needed']))}")
            
            st.markdown(f"**💡 Specific Offers:**")
            for offer in strategy.get('offers', ['Custom offers needed']):
                st.markdown(f"• {offer}")
            
            st.markdown(f"**⏰ Optimal Timing:**")
            st.markdown(f"{strategy.get('timing', 'Custom timing strategy needed')}")
            
            st.markdown("---")
        
        # Campaign performance predictor
        st.subheader("📈 Campaign Performance Predictor")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Estimated Campaign Reach:**")
            total_customers = len(filtered_df)
            estimated_reach = min(total_customers * 0.8, total_customers)  # 80% reach rate
            st.metric("Potential Customers Reached", f"{estimated_reach:,.0f}")
            
            st.markdown("**Expected Response Rates by Segment:**")
            response_rates = {
                "Bulk Dry Shoppers – Urban": 0.15,
                "Bulk Dry Shoppers – Suburban": 0.12,
                "Fresh-Focused Families – Urban": 0.18,
                "Fresh-Focused Families – Suburban": 0.16,
                "Balanced Shoppers – Urban": 0.14,
                "Balanced Shoppers – Suburban": 0.13
            }
            
            for cluster in selected_clusters:
                cluster_size = len(filtered_df[filtered_df['cluster_name'] == cluster])
                response_rate = response_rates.get(cluster, 0.14)
                expected_responses = cluster_size * response_rate
                st.metric(f"{cluster[:20]}...", f"{expected_responses:.0f} responses")
        
        with col2:
            st.markdown("**ROI Projections:**")
            avg_order_increase = 1.25  # 25% increase in average order
            current_avg = filtered_df['total_sales'].mean()
            projected_avg = current_avg * avg_order_increase
            additional_revenue = (projected_avg - current_avg) * estimated_reach * 0.14  # 14% avg response rate
            
            st.metric("Current Avg Order Value", f"Rs.{current_avg:.2f}")
            st.metric("Projected Avg Order Value", f"Rs.{projected_avg:.2f}")
            st.metric("Estimated Additional Revenue", f"Rs.{additional_revenue:,.2f}")
            
            # Campaign budget suggestion
            suggested_budget = additional_revenue * 0.3  # 30% of additional revenue
            st.metric("Suggested Campaign Budget", f"Rs.{suggested_budget:,.2f}")
        
        # Action items
        st.subheader("🎯 Immediate Action Items")
        
        action_items = []
        
        if "Urban" in [area for area in selected_areas]:
            action_items.append("🏙️ **Urban Focus**: Enhance mobile app features and push notifications")
        
        if "Sub Urban" in [area for area in selected_areas]:
            action_items.append("🏡 **Suburban Focus**: Strengthen delivery services and local partnerships")
        
        if any("Fresh-Focused" in cluster for cluster in selected_clusters):
            action_items.append("🥬 **Fresh Strategy**: Implement daily fresh deals and recipe recommendations")
        
        if any("Bulk Dry" in cluster for cluster in selected_clusters):
            action_items.append("📦 **Bulk Strategy**: Create subscription services and bulk discount programs")
        
        if any("Balanced" in cluster for cluster in selected_clusters):
            action_items.append("⚖️ **Balanced Strategy**: Develop cross-category promotion engine")
        
        for item in action_items:
            st.markdown(item)
        
        # Campaign timeline
        st.subheader("📅 Suggested Campaign Timeline")
        
        timeline_data = {
            "Week": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "Activity": [
                "Campaign setup & audience targeting",
                "Launch primary strategies",
                "Monitor & optimize",
                "Analyze results & plan next phase"
            ],
            "Focus": [
                "Data preparation & creative development",
                "Multi-channel campaign launch",
                "Performance tracking & A/B testing",
                "ROI analysis & strategy refinement"
            ]
        }
        
        timeline_df = pd.DataFrame(timeline_data)
        st.dataframe(timeline_df, use_container_width=True, hide_index=True)

    # Footer
    st.markdown("---")
    st.markdown(f"*Dashboard last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data refreshes every 5 minutes*")

if __name__ == "__main__":
    main()