-- Add business name and pain points fields to assistant_leads table
-- This enhances the lead capture for signup requests

ALTER TABLE assistant_leads 
ADD COLUMN IF NOT EXISTS business_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
ADD COLUMN IF NOT EXISTS pain_points TEXT,
ADD COLUMN IF NOT EXISTS lead_source VARCHAR(50) DEFAULT 'signup_form';

-- Add index for lead source
CREATE INDEX IF NOT EXISTS assistant_leads_source_idx ON assistant_leads(lead_source);

COMMENT ON COLUMN assistant_leads.business_name IS 'Company/business name of the lead';
COMMENT ON COLUMN assistant_leads.phone IS 'Phone number for contact';
COMMENT ON COLUMN assistant_leads.pain_points IS 'Business challenges and pain points described by the lead';
COMMENT ON COLUMN assistant_leads.lead_source IS 'Source of lead: signup_form, assistant_widget, etc';

